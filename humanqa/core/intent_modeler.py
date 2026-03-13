"""Product Intent Modeler.

Builds a Product Intent Model from visible product surfaces (landing page,
onboarding, help docs, app store description, UI copy) and user-provided context.
No code inspection.
"""

from __future__ import annotations

import logging

from humanqa.core.llm import LLMClient
from humanqa.core.schemas import ProductIntentModel, InstitutionalRelevance, RunConfig

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """You are a product analyst for HumanQA, an AI QA evaluation system.

Your job is to understand what a product IS and DOES by examining its visible surfaces only.
You must NEVER reference source code, repos, or internal architecture.

You will receive:
- Page content scraped from the product's landing/home page
- Any user-supplied brief or context
- Optional focus flows and persona hints

From this, infer:
- product_name: The product's name
- product_type: Category (e.g. "B2B SaaS dashboard", "consumer marketplace", "developer tool")
- target_audience: Who this is for (list of audience segments)
- primary_jobs: What users hire this product to do (list of jobs-to-be-done)
- user_expectations: What users would reasonably expect from a product like this
- critical_journeys: The most important user flows to test
- trust_sensitive_actions: Actions where trust, accuracy, or safety matter most
- institutional_relevance: "none" | "low" | "moderate" | "high" — would serious professionals/institutions use this?
- institutional_reasoning: Why you assigned that relevance level
- assumptions: What you're assuming that could be wrong
- confidence: 0.0-1.0 how confident you are in this model

Respond with valid JSON matching the schema exactly."""

INTENT_PROMPT_TEMPLATE = """Analyze this product and build a Product Intent Model.

## Product URL
{url}

## Scraped Landing Page Content
{page_content}

## User-Supplied Brief
{brief}

## Focus Flows (if any)
{focus_flows}

## Persona Hints (if any)
{persona_hints}

Respond with a JSON object with these fields:
product_name, product_type, target_audience (list), primary_jobs (list),
user_expectations (list), critical_journeys (list), trust_sensitive_actions (list),
institutional_relevance ("none"|"low"|"moderate"|"high"), institutional_reasoning (string),
assumptions (list), confidence (float 0-1)."""


class IntentModeler:
    """Infers product purpose from visible surfaces."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def build_intent_model(
        self,
        config: RunConfig,
        page_content: str,
    ) -> ProductIntentModel:
        """Build a Product Intent Model from scraped content and config."""
        prompt = INTENT_PROMPT_TEMPLATE.format(
            url=config.target_url,
            page_content=page_content[:12000],  # Cap to avoid token overflow
            brief=config.brief or "(none provided)",
            focus_flows=", ".join(config.focus_flows) if config.focus_flows else "(none)",
            persona_hints=", ".join(config.persona_hints) if config.persona_hints else "(none)",
        )

        logger.info("Building product intent model for %s", config.target_url)

        try:
            data = self.llm.complete_json(prompt, system=INTENT_SYSTEM_PROMPT)
            # Map institutional_relevance string to enum
            ir_raw = data.get("institutional_relevance", "none")
            data["institutional_relevance"] = InstitutionalRelevance(ir_raw)
            model = ProductIntentModel(**data)
            logger.info(
                "Intent model built: %s (%s), confidence=%.2f",
                model.product_name,
                model.product_type,
                model.confidence,
            )
            return model
        except Exception as e:
            logger.error("Failed to build intent model: %s", e)
            # Return a minimal model so the pipeline can continue
            return ProductIntentModel(
                product_name="Unknown",
                product_type="Unknown",
                confidence=0.1,
                assumptions=["Intent modeling failed; using minimal defaults"],
            )
