from groq import AsyncGroq


class LLMClient:
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "llama-3.1-70b-versatile",
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""
