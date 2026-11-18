"""AI Analyst: calls Claude with the server's API key and meters usage per organisation."""
from __future__ import annotations

from typing import Callable, Optional

import anthropic

from config.settings import get_settings
from services import usage

SYSTEM_PROMPT = """You are AeroVia's AI Aviation Analyst, an expert in Indian domestic airline economics: RASK/CASK/BELF frameworks, ATF pricing dynamics, DGCA regulations, yield management, and Indian aviation market structure (IndiGo, Air India, SpiceJet, Akasa, the UDAN scheme, slot constraints at metro airports).

When route data is provided in the context below, reference it directly in your analysis.
Be concise, data-driven, and actionable. Use ₹ for currency. Format key numbers clearly (₹12.5L, 82% LF, 14.2p RASK).
For route analyses, structure your response as: Revenue Assessment → Cost Drivers → Profitability Verdict → Key Risks → Recommendations."""

MAX_TOKENS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnalystError(Exception):
    """Raised with a message that is safe to show to the user."""


class AnalystNotConfigured(AnalystError):
    pass


class QuotaExceeded(AnalystError):
    pass


def _default_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key)


def ask(org_id: int, user_id: Optional[int], messages: list[dict], context: str = "",
        client_factory: Callable[[], anthropic.Anthropic] = _default_client) -> str:
    """Send the conversation to Claude and return the reply text.

    `messages` is the chat history as [{"role": "user"|"assistant", "content": str}, ...].
    """
    settings = get_settings()
    if not settings.ai_configured:
        raise AnalystNotConfigured(
            "The AI Analyst isn't configured on this server yet (no Anthropic API key set)."
        )

    quota = usage.ai_quota(org_id)
    if quota.exhausted:
        raise QuotaExceeded(
            f"Your organisation has used all {quota.limit} AI Analyst messages for this month. "
            "Upgrade your plan or wait until the 1st."
        )

    system = SYSTEM_PROMPT + (f"\n\n--- LIVE ROUTE DATA ---\n{context}" if context else "")
    try:
        response = client_factory().beta.messages.create(
            model=settings.claude_model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=messages,
            output_config={"effort": settings.claude_effort},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise AnalystError("The AI service rejected the server's API key. Contact your administrator.") from e
    except anthropic.RateLimitError as e:
        raise AnalystError("The AI service is busy right now. Please try again in a minute.") from e
    except anthropic.BadRequestError as e:
        raise AnalystError("The AI service couldn't process this request.") from e
    except anthropic.APIStatusError as e:
        raise AnalystError("The AI service had a problem. Please try again shortly.") from e
    except anthropic.APIConnectionError as e:
        raise AnalystError("Couldn't reach the AI service. Check the server's network connection.") from e

    u = response.usage
    usage.record(org_id, user_id, usage.AI_MESSAGE, model=response.model,
                 input_tokens=getattr(u, "input_tokens", 0), output_tokens=getattr(u, "output_tokens", 0))

    if response.stop_reason == "refusal":
        return "I can't help with that request. Try rephrasing it as a question about route economics."

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if response.stop_reason == "max_tokens":
        text += "\n\n_(Response was cut off at the length limit.)_"
    return text or "I didn't produce an answer that time. Please try again."
