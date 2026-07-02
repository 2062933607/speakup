"""直接测试新 Key 的 Whisper"""
import struct, math, os
from openai import OpenAI
from pathlib import Path

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

# 简短 WAV
r = 16000; d = 1.0; n = int(r*d)
h = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36+n*2, b'WAVE', b'fmt ', 16, 1, 1, r, r*2, 2, 16, b'data', n*2)
w = h + b''.join(struct.pack('<h', int(200*math.sin(2*math.pi*440*i/r))) for i in range(n))

with open("_t.wav", "wb") as f: f.write(w)

try:
    c = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    with open("_t.wav", "rb") as f:
        t = c.audio.transcriptions.create(model="whisper-large-v3", file=f, response_format="text", language="en")
    result = f"Whisper OK: '{t.strip()}'"
except Exception as e:
    result = f"Whisper FAIL: {e}"
finally:
    os.unlink("_t.wav")

with open("whisper_test.txt", "w") as f: f.write(result)
