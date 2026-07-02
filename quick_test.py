import requests, json

BASE = "http://localhost:8080"

# 启动对话
r = requests.post(f"{BASE}/api/chat/start?character_id=alex", timeout=15)
cid = r.json()["conversation_id"]

# 发送文字
r2 = requests.post(f"{BASE}/api/chat/send", json={"conversation_id": cid, "text": "hi"}, timeout=20)
reply = r2.json()["assistant_message"]["text"]

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(f"Start: 200\nReply: {reply}\n")

print("done")
