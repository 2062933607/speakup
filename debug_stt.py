"""测试 STT service 并打印详细错误"""
import asyncio, sys, struct, math, os
sys.path.insert(0, ".")

# 强制重新加载 .env
from pathlib import Path
env_path = Path(".") / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            os.environ[k] = v

# 重新加载 config
import importlib
import backend.config
importlib.reload(backend.config)
from backend.config import settings

results = []
results.append(f"Provider: {settings.stt_provider}")
results.append(f"Key prefix: {settings.groq_api_key[:15]}...")

# 重新导入 stt_service
import backend.services.stt_service as stt_svc
importlib.reload(stt_svc)

# 生成测试 WAV
r = 16000
n = int(r * 1.0)
h = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36+n*2, b'WAVE', b'fmt ', 16, 1, 1, r, r*2, 2, 16, b'data', n*2)
w = h + b''.join(struct.pack('<h', int(200*math.sin(2*math.pi*440*i/r))) for i in range(n))

async def test():
    try:
        result = await stt_svc.speech_to_text(w, "wav")
        results.append(f"Result: {result}")
    except Exception as e:
        results.append(f"Error: {e}")

asyncio.run(test())

with open("debug_stt.txt", "w") as f:
    f.write("\n".join(results))
