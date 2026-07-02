"""语音合成服务 (TTS)"""
import asyncio
import io
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

# Edge TTS voice 映射
VOICE_MAP = {
    "american_male": "en-US-GuyNeural",
    "american_female": "en-US-JennyNeural",
    "british_male": "en-GB-RyanNeural",
    "british_female": "en-GB-SoniaNeural",
    "australian_female": "en-AU-NatashaNeural",
    "australian_male": "en-AU-WilliamNeural",
}

TTS_TIMEOUT = 5  # TTS 请求超时秒数


async def text_to_speech(text: str, voice: str = "american_female") -> bytes | None:
    """将文字转为语音，返回音频二进制数据。失败时返回 None。"""
    if settings.tts_provider == "openai" and settings.openai_api_key:
        try:
            return await asyncio.wait_for(_openai_tts(text), timeout=TTS_TIMEOUT)
        except (Exception, asyncio.TimeoutError) as e:
            logger.warning(f"OpenAI TTS failed: {e}, falling back to Edge TTS")
            try:
                return await asyncio.wait_for(_edge_tts(text, voice), timeout=TTS_TIMEOUT)
            except (Exception, asyncio.TimeoutError) as e2:
                logger.warning(f"Edge TTS also failed: {e2}")
                return None
    else:
        try:
            return await asyncio.wait_for(_edge_tts(text, voice), timeout=TTS_TIMEOUT)
        except (Exception, asyncio.TimeoutError) as e:
            logger.warning(f"Edge TTS failed: {e}")
            if settings.openai_api_key:
                try:
                    return await asyncio.wait_for(_openai_tts(text), timeout=TTS_TIMEOUT)
                except (Exception, asyncio.TimeoutError) as e2:
                    logger.warning(f"OpenAI TTS also failed: {e2}")
            return None


async def _edge_tts(text: str, voice: str) -> bytes:
    """使用 Edge TTS (免费)"""
    import edge_tts

    voice_name = VOICE_MAP.get(voice, "en-US-JennyNeural")
    communicate = edge_tts.Communicate(text, voice_name)
    audio_bytes = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.write(chunk["data"])
    return audio_bytes.getvalue()


async def _openai_tts(text: str) -> bytes:
    """使用 OpenAI TTS"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    response = await client.audio.speech.create(
        model="tts-1",
        voice=settings.openai_tts_voice,
        input=text,
    )
    return response.content
