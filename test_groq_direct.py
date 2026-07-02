"""直接测试 Groq Whisper API"""
import struct, math, sys
from openai import OpenAI
from pathlib import Path
import os, tempfile

# Load .env manually
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
results.append(f"Key prefix: {api_key[:12]}...")
results.append(f"Key length: {len(api_key)}")

# 简短 WAV
sample_rate = 16000
duration = 1.0
num_samples = int(sample_rate * duration)
wav_header = struct.pack(
    '<4sI4s4sIHHIIHH4sI',
    b'RIFF', 36 + num_samples * 2,
    b'WAVE', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
    b'data', num_samples * 2
)
samples = b''.join(struct.pack('<h', int(200 * math.sin(2 * math.pi * 440 * i / sample_rate))) for i in range(num_samples))
wav_data = wav_header + samples

with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
    f.write(wav_data)
    tmp = f.name

try:
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    with open(tmp, 'rb') as f:
        result = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
            response_format="text",
            language="en",
        )
    results.append(f"Result: '{result.strip()}'")
    results.append("SUCCESS")
except Exception as e:
    results.append(f"Error: {e}")
finally:
    os.unlink(tmp)

with open("groq_direct.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
