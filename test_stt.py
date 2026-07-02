"""测试 Groq STT 语音识别"""
import requests, json, sys

BASE = "http://localhost:8080"

# 1) 启动对话
r = requests.post(f"{BASE}/api/chat/start?character_id=alex", timeout=15)
assert r.status_code == 200, f"Start failed: {r.status_code}"
cid = r.json()["conversation_id"]
print(f"[1] 对话已启动: {cid}")

# 2) 制造一段简单音频（1kHz 正弦波，里面没语音，就测试管道）
# 用 Python 生成一个小 WAV 文件发给 send-voice
import struct, math

sample_rate = 16000
duration = 1.0  # 1秒
num_samples = int(sample_rate * duration)

wav_header = struct.pack(
    '<4sI4s4sIHHIIHH4sI',
    b'RIFF', 36 + num_samples * 2,
    b'WAVE',
    b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
    b'data', num_samples * 2
)

# 生成静音+一点点噪音
samples = b''
for i in range(num_samples):
    val = int(200 * math.sin(2 * math.pi * 1000 * i / sample_rate))
    samples += struct.pack('<h', val)

wav_data = wav_header + samples

# 3) 发送到 send-voice
files = {"audio": ("test.wav", wav_data, "audio/wav")}
data = {"conversation_id": cid}
r2 = requests.post(f"{BASE}/api/chat/send-voice", files=files, data=data, timeout=30)
d2 = r2.json()
print(f"[2] send-voice status: {r2.status_code}")
print(f"    User message: {d2.get('user_message', {}).get('text', 'N/A')}")
print(f"    Assistant reply: {d2.get('assistant_message', {}).get('text', 'N/A')[:80]}")
print(f"\n{'✅ 语音识别管道正常工作!' if r2.status_code == 200 and 'Speech recognition' not in d2.get('user_message',{}).get('text','') else '⚠️ STT 返回了错误占位符（正常，测试音频无语音）'}")
