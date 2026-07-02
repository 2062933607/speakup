"""检测后端当前 STT 配置"""
import requests, json

r = requests.get("http://localhost:8080/api/characters", timeout=5)
print(f"API status: {r.status_code}")

# 直接测试后端 env 中加载的 key
import sys
sys.path.insert(0, ".")
from backend.config import Settings

s = Settings()
with open("cfg_test.txt", "w") as f:
    f.write(f"stt_provider: {s.stt_provider}\n")
    f.write(f"groq_key_prefix: {s.groq_api_key[:15] if s.groq_api_key else 'EMPTY'}...\n")
    f.write(f"whisper_model: {s.whisper_model}\n")
