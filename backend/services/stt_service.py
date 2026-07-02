"""语音识别服务 (STT) — 支持 Groq Whisper (免费) 和 OpenAI Whisper"""
import asyncio
import logging
import tempfile
import os
from openai import AsyncOpenAI
from backend.config import settings

logger = logging.getLogger(__name__)

STT_TIMEOUT = 15  # STT 请求超时秒数


def _get_stt_client() -> AsyncOpenAI | None:
    """根据配置返回 STT 客户端。无 API Key 时返回 None。"""
    if settings.stt_provider == "groq":
        if not settings.groq_api_key or settings.groq_api_key == "gsk_your-groq-api-key":
            return None
        return AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
    elif settings.stt_provider == "openai":
        if not settings.openai_api_key or settings.openai_api_key == "sk-your-api-key-here":
            return None
        return AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return None


async def speech_to_text(audio_data: bytes, audio_format: str = "webm") -> str:
    """将音频数据转为文字。无 API Key 时返回提示文字。"""
    client = _get_stt_client()
    if client is None:
        provider = settings.stt_provider
        logger.info(f"No API key configured for STT provider '{provider}'")
        return "[Speech recognition needs an API key. Please type your message instead.]"

    try:
        return await asyncio.wait_for(
            _call_whisper(client, audio_data, audio_format),
            timeout=STT_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.warning("STT request timed out")
        return "[Speech recognition timed out. Please try again.]"
    except Exception as e:
        logger.warning(f"STT failed: {e}")
        return "[Speech recognition failed. Please type your message instead.]"


async def _call_whisper(client: AsyncOpenAI, audio_data: bytes, audio_format: str) -> str:
    suffix_map = {"webm": ".webm", "wav": ".wav", "mp3": ".mp3", "ogg": ".ogg", "m4a": ".m4a"}
    suffix = suffix_map.get(audio_format, ".webm")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=f,
                response_format="text",
                language="en",
            )
        return transcript.strip()
    finally:
        os.unlink(tmp_path)
