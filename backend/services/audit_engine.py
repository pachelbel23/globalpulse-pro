import json

from models.audit import AuditRequest, SWOTReport
from services.llm_client import LLMClient

SYSTEM_PROMPT = (
    "You are a business model analyst. Respond ONLY with valid JSON containing "
    "exactly these keys: strengths (list of strings), weaknesses (list of strings), "
    "opportunities (list of strings), threats (list of strings), risk_summary (string). "
    "Do not include any text outside the JSON object."
)


class AuditEngine:
    def __init__(self, api_key: str):
        self._llm = LLMClient(api_key=api_key)

    async def _call_llm(self, prompt: str) -> str:
        return await self._llm.chat(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)

    async def analyze(self, request: AuditRequest) -> SWOTReport:
        prompt = (
            f"Perform a SWOT analysis for the following business model.\n\n"
            f"Business description: {request.model_description}\n"
            f"Target market: {request.target_market}\n"
            f"Industry: {request.industry}\n"
        )
        raw = await self._call_llm(prompt)
        try:
            data = json.loads(raw)
            return SWOTReport(**data)
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            raise ValueError(f"Failed to parse LLM response: {exc}") from exc
