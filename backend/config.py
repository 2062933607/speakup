"""应用配置管理"""
import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv():
    """手动加载 .env 文件"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value


_load_dotenv()


@dataclass
class Settings:
    # LLM 配置 (DeepSeek / OpenAI 兼容)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # STT 语音识别提供商: groq (免费) / openai
    stt_provider: str = os.getenv("STT_PROVIDER", "groq")
    whisper_model: str = os.getenv("WHISPER_MODEL", "whisper-large-v3")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    # TTS 提供商
    tts_provider: str = os.getenv("TTS_PROVIDER", "edge")
    openai_tts_voice: str = os.getenv("OPENAI_TTS_VOICE", "alloy")

    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
