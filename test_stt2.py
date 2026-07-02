"""测试 Groq Whisper STT"""
import requests, struct, math

BASE = "http://localhost:8080"

# 生成测试 WAV
sample_rate = 16000
duration = 1.0
num_samples = int(sample_rate * duration)

wav_header = struct.pack(
    '<4sI4s4sIHHIIHH4sI',
    b'RIFF', 36 + num_samples * 2,
    b'WAVE',
    b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
    b'data', num_samples * 2
)
samples = b''.join(struct.pack('<h', int(200 * math.sin(2 * math.pi * 440 * i / sample_rate))) for i in range(num_samples))
wav_data = wav_header + samples

# 启动对话
r = requests.post(f"{BASE}/api/chat/start?character_id=alex", timeout=15)
cid = r.json()["conversation_id"]

# 发送语音
files = {"audio": ("test.wav", wav_data, "audio/wav")}
r2 = requests.post(f"{BASE}/api/chat/send-voice", files=files, data={"conversation_id": cid}, timeout=30)
d2 = r2.json()

with open("stt_result.txt", "w", encoding="utf-8") as f:
    user_text = d2["user_message"]["text"]
    ai_text = d2["assistant_message"]["text"]
    f.write(f"Status: {r2.status_code}\n")
    f.write(f"User (STT result): {user_text}\n")
    f.write(f"AI reply: {ai_text}\n")
    f.write(f"\nSTT working: {'yes' if not user_text.startswith('[') else 'no (placeholder)'}\n")

print("done")
