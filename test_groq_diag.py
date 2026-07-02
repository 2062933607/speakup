"""测试 Groq API - 诊断问题"""
from openai import OpenAI
from pathlib import Path
import os

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k not in os.environ:
                os.environ[k] = v

api_key = os.getenv("GROQ_API_KEY", "")
results = []

client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# 测试 1: 聊天 API
try:
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'hello' in one word"}],
        max_tokens=10,
    )
    results.append(f"Chat API: OK - {r.choices[0].message.content}")
except Exception as e:
    results.append(f"Chat API: FAIL - {e}")

# 测试 2: 模型列表
try:
    models = client.models.list()
    whisper_models = [m.id for m in models if "whisper" in m.id]
    results.append(f"Whisper models available: {whisper_models if whisper_models else 'NONE'}")
except Exception as e:
    results.append(f"Models list: FAIL - {e}")

with open("groq_diag.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
