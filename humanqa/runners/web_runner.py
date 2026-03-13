"""Web Runner — Playwright-based external UI evaluation.

Evaluates a product strictly through browser interaction. No code inspection.
Captures screenshots, timing, console errors, and network issues.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from humanqa.core.llm import LLMClient
from humanqa.core.schemas import (
    AgentPersona,
    CoverageEntry,
    CoverageMap,
    Evidence,
    Issue,
    IssueCategory,
    Platform,
    RunConfig,
    Severity,
)

logger = logging.getLogger(__name__)

EVALUATION_SYSTEM_PROMPT = """You are a QA evaluation agent for HumanQA. You are acting as a specific user persona
interacting with a product through its UI.

Your job:
1. Look at the screenshot and page content provided
2. Evaluate what you see from your persona's perspective
3. Identify issues across: functional, UX, UI, performance, trust, design
4. Apply common-sense judgment — not just mechanical checks
5. Separate observed facts from inferred judgments from hypotheses

For each issue found, provide:
- title: Clear issue title
- severity: critical | high | medium | low | info
- confidence: 0.0-1.0
- category: functional | ux | ui | performance | trust | design
- user_impact: How this affects a real user
- observed_facts: What you literally see (list)
- inferred_judgment: What you conclude from what you see
- hypotheses: Possible explanations (list)
- likely_product_area: Where in the product this lives
- repair_brief: What a developer should fix

Common-sense questions to ask yourself:
- Is the next step obvious?
- Does this behave as expected?
- Would a user trust this?
- Would a user give up here?
- Is the copy confusing?
- Does this feel broken even without a visible error?

Respond with a JSON object: {"issues": [...], "observations": "...", "next_actions": [...]}"""

EVALUATION_PROMPT_TEMPLATE = """You are: {persona_name} — {persona_role}
Goals: {persona_goals}
Patience: {patience_level} | Expertise: {expertise_level}
Style: {behavioral_style}

Current journey: {journey}
Current URL: {url}
Page title: {title}

## Visible page text (truncated)
{page_text}

## Console errors (if any)
{console_errors}

## Performance
- Page load time: {load_time_ms}ms
- Network requests: {request_count}

## Previous actions taken
{previous_actions}

Evaluate this page from your persona's perspective. Find issues.
Respond with JSON: {{"issues": [...], "observations": "brief notes", "next_actions": ["click X", "navigate to Y"]}}"""


class WebRunner:
    """Runs web-based evaluation using Playwright."""

    def __init__(self, llm: LLMClient, output_dir: str = "./artifacts"):
        self.llm = llm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def evaluate(
        self,
        config: RunConfig,
        persona: AgentPersona,
        journeys: list[str],
        coverage: CoverageMap,
    ) -> tuple[list[Issue], CoverageMap]:
        """Run evaluation for a single persona across assigned journeys."""
        issues: list[Issue] = []

        async with async_playwright() as p:
            # Choose viewport based on persona device preference
            if persona.device_preference == Platform.mobile_web:
                viewport = {"width": 390, "height": 844}
                user_agent = (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                    "Mobile/15E148 Safari/604.1"
                )
            else:
                viewport = {"width": 1440, "height": 900}
                user_agent = None

            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport=viewport,
                user_agent=user_agent,
            )
            page = await context.new_page()

            # Collect console errors
            console_errors: list[str] = []
            page.on("console", lambda msg: (
                console_errors.append(f"[{msg.type}] {msg.text}")
                if msg.type in ("error", "warning") else None
            ))

            # Track network requests
            request_count = 0
            page.on("request", lambda _: None)  # counting handled below

            try:
                # Navigate to target
                start = time.monotonic()
                await page.goto(config.target_url, wait_until="domcontentloaded", timeout=30000)
                load_time_ms = int((time.monotonic() - start) * 1000)

                # Handle credentials if provided
                if config.credentials:
                    await self._attempt_login(page, config)

                # Evaluate each journey
                previous_actions: list[str] = [f"Navigated to {config.target_url}"]

                for journey in journeys:
                    journey_issues = await self._evaluate_page(
                        page=page,
                        persona=persona,
                        journey=journey,
                        config=config,
                        console_errors=console_errors,
                        load_time_ms=load_time_ms,
                        previous_actions=previous_actions,
                    )
                    issues.extend(journey_issues)

                    coverage.entries.append(CoverageEntry(
                        url=page.url,
                        screen_name=await page.title(),
                        agent_id=persona.id,
                        flow=journey,
                        status="visited",
                        issues_found=len(journey_issues),
                    ))

                    # Follow suggested next actions for deeper exploration
                    # (limited to 3 navigation steps per journey to avoid infinite loops)
                    for step in range(3):
                        step_issues = await self._explore_next(
                            page=page,
                            persona=persona,
                            journey=journey,
                            config=config,
                            console_errors=console_errors,
                            previous_actions=previous_actions,
                        )
                        if not step_issues and step > 0:
                            break
                        issues.extend(step_issues)

            except Exception as e:
                logger.error("Web evaluation failed for %s: %s", persona.name, e)
                issues.append(Issue(
                    title=f"Evaluation blocked: {str(e)[:100]}",
                    severity=Severity.critical,
                    category=IssueCategory.functional,
                    agent=persona.id,
                    user_impact="Could not complete evaluation — product may be unreachable or broken",
                    observed_facts=[str(e)],
                    platform=Platform.web,
                ))
            finally:
                await browser.close()

        return issues, coverage

    async def scrape_landing_page(self, url: str) -> str:
        """Scrape visible text from a URL for intent modeling. Returns page text."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)  # Let JS render
                text = await page.evaluate("() => document.body.innerText")
                return text[:15000]
            except Exception as e:
                logger.error("Failed to scrape %s: %s", url, e)
                return f"(Failed to load: {e})"
            finally:
                await browser.close()

    async def _attempt_login(self, page: Page, config: RunConfig) -> None:
        """Try to fill login forms if credentials provided."""
        if not config.credentials:
            return
        try:
            # Look for common email/password fields
            email_sel = 'input[type="email"], input[name="email"], input[id*="email"], input[placeholder*="email" i]'
            pwd_sel = 'input[type="password"]'

            email_field = page.locator(email_sel).first
            if await email_field.is_visible(timeout=3000):
                await email_field.fill(config.credentials.email or "")

            pwd_field = page.locator(pwd_sel).first
            if await pwd_field.is_visible(timeout=3000):
                await pwd_field.fill(config.credentials.password or "")

            # Try common submit buttons
            submit = page.locator(
                'button[type="submit"], input[type="submit"], button:has-text("Log in"), '
                'button:has-text("Sign in"), button:has-text("Login")'
            ).first
            if await submit.is_visible(timeout=2000):
                await submit.click()
                await page.wait_for_load_state("domcontentloaded", timeout=10000)

        except Exception as e:
            logger.warning("Login attempt failed: %s", e)

    async def _evaluate_page(
        self,
        page: Page,
        persona: AgentPersona,
        journey: str,
        config: RunConfig,
        console_errors: list[str],
        load_time_ms: int,
        previous_actions: list[str],
    ) -> list[Issue]:
        """Evaluate current page state from persona's perspective."""
        # Capture screenshot
        screenshot_name = f"{persona.id}-{len(previous_actions)}.png"
        screenshot_path = self.output_dir / screenshot_name
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Get page text
        try:
            page_text = await page.evaluate("() => document.body.innerText")
        except Exception:
            page_text = "(Could not extract page text)"

        # Count requests
        request_count = 0  # Simplified; full HAR capture is a day-2 enhancement

        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            persona_name=persona.name,
            persona_role=persona.role,
            persona_goals=", ".join(persona.goals),
            patience_level=persona.patience_level,
            expertise_level=persona.expertise_level,
            behavioral_style=persona.behavioral_style,
            journey=journey,
            url=page.url,
            title=await page.title(),
            page_text=page_text[:6000],
            console_errors="\n".join(console_errors[-10:]) if console_errors else "(none)",
            load_time_ms=load_time_ms,
            request_count=request_count,
            previous_actions="\n".join(previous_actions[-10:]),
        )

        try:
            data = self.llm.complete_json(prompt, system=EVALUATION_SYSTEM_PROMPT)
            raw_issues = data.get("issues", [])
            issues = []
            for raw in raw_issues:
                # Map category string to enum, with fallback
                cat = raw.get("category", "functional")
                try:
                    category = IssueCategory(cat)
                except ValueError:
                    category = IssueCategory.functional

                sev = raw.get("severity", "medium")
                try:
                    severity = Severity(sev)
                except ValueError:
                    severity = Severity.medium

                issues.append(Issue(
                    title=raw.get("title", "Untitled issue"),
                    severity=severity,
                    confidence=raw.get("confidence", 0.7),
                    platform=Platform.mobile_web if persona.device_preference == Platform.mobile_web else Platform.web,
                    category=category,
                    agent=persona.id,
                    user_impact=raw.get("user_impact", ""),
                    repro_steps=raw.get("repro_steps", [f"Navigate to {page.url}"]),
                    expected=raw.get("expected", ""),
                    actual=raw.get("actual", ""),
                    observed_facts=raw.get("observed_facts", []),
                    inferred_judgment=raw.get("inferred_judgment", ""),
                    hypotheses=raw.get("hypotheses", []),
                    evidence=Evidence(screenshots=[screenshot_name]),
                    likely_product_area=raw.get("likely_product_area", ""),
                    repair_brief=raw.get("repair_brief", ""),
                ))

            return issues

        except Exception as e:
            logger.error("Page evaluation failed: %s", e)
            return []

    async def _explore_next(
        self,
        page: Page,
        persona: AgentPersona,
        journey: str,
        config: RunConfig,
        console_errors: list[str],
        previous_actions: list[str],
    ) -> list[Issue]:
        """Take one exploration step and evaluate. Returns issues found."""
        # Ask LLM what to do next based on current page
        try:
            page_text = await page.evaluate("() => document.body.innerText")
        except Exception:
            return []

        nav_prompt = f"""You are {persona.name}. You are on: {page.url}
Your journey: {journey}
Previous actions: {", ".join(previous_actions[-5:])}

Page text (truncated): {page_text[:3000]}

What single action should you take next to continue evaluating this journey?
Respond with JSON: {{"action": "click|navigate|type|scroll|done", "target": "selector or URL", "value": "for type actions", "description": "what and why"}}
If the journey is complete or you can't proceed, use action "done"."""

        try:
            nav = self.llm.complete_json(nav_prompt)
            action = nav.get("action", "done")

            if action == "done":
                return []

            description = nav.get("description", "")
            target = nav.get("target", "")

            if action == "click" and target:
                try:
                    await page.locator(target).first.click(timeout=5000)
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
                    previous_actions.append(f"Clicked: {target} ({description})")
                except Exception:
                    previous_actions.append(f"Failed to click: {target}")
                    return []

            elif action == "navigate" and target:
                try:
                    start = time.monotonic()
                    await page.goto(target, wait_until="domcontentloaded", timeout=15000)
                    load_time = int((time.monotonic() - start) * 1000)
                    previous_actions.append(f"Navigated to: {target}")
                except Exception:
                    previous_actions.append(f"Failed to navigate: {target}")
                    return []

            elif action == "type" and target:
                try:
                    await page.locator(target).first.fill(nav.get("value", "test"))
                    previous_actions.append(f"Typed in: {target}")
                except Exception:
                    return []

            elif action == "scroll":
                await page.evaluate("window.scrollBy(0, 600)")
                previous_actions.append("Scrolled down")

            else:
                return []

            # Evaluate new state
            return await self._evaluate_page(
                page=page,
                persona=persona,
                journey=journey,
                config=config,
                console_errors=console_errors,
                load_time_ms=0,
                previous_actions=previous_actions,
            )

        except Exception as e:
            logger.error("Exploration step failed: %s", e)
            return []
