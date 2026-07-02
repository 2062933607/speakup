"""大模型对话服务"""
import logging
from openai import AsyncOpenAI
from backend.config import settings

logger = logging.getLogger(__name__)
_client: AsyncOpenAI | None = None

# 无 API Key 时的模拟回复
FALLBACK_REPLIES = [
    "That's interesting! Tell me more about it.",
    "I see! What do you think about that?",
    "Good point! Could you elaborate a bit?",
    "Oh really? How does that make you feel?",
    "I understand. Can you give me an example?",
    "That makes sense. What happened next?",
    "I appreciate you sharing that. Let's keep talking!",
    "That's a great perspective. Have you always felt that way?",
]


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return _client


async def chat(
    system_prompt: str,
    messages: list[dict],
    user_message: str,
) -> str:
    """发送对话请求到 LLM，返回助手回复。无 API Key 时返回模拟回复。"""
    if not settings.openai_api_key or settings.openai_api_key == "sk-your-api-key-here":
        logger.info("No API key configured, using fallback reply")
        # 返回一个适合上下文的模拟回复
        import random
        return random.choice(FALLBACK_REPLIES)

    try:
        client = get_client()
        chat_messages = [{"role": "system", "content": system_prompt}]
        chat_messages.extend(messages)
        chat_messages.append({"role": "user", "content": user_message})

        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=chat_messages,
            temperature=0.8,
            max_tokens=300,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"LLM API call failed: {e}, using fallback")
        import random
        return random.choice(FALLBACK_REPLIES)
