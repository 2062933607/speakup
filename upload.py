import requests, base64, os, sys
from pathlib import Path

GH = sys.argv[1]
TK = sys.argv[2]
H = {"Authorization": f"token {TK}", "Accept": "application/vnd.github.v3+json"}
API = "https://api.github.com"
log = []

def L(msg):
    log.append(msg)
    print(msg)

# 收集文件
L("Collecting files...")
root = Path(".")
files = []
for dp, dn, fs in os.walk(root):
    dn[:] = [d for d in dn if d not in {"node_modules","__pycache__",".git","dist"} and not d.startswith(".")]
    for f in fs:
        if f in {"upload_to_github.py", ".env"}: continue
        fp = Path(dp) / f
        if fp.suffix in {".pyc",".log"}: continue
        rel = fp.relative_to(root).as_posix()
        files.append((str(fp), rel))

L(f"Total: {len(files)} files")

# 按文件上传
ok = 0
for i, (fp, rel) in enumerate(files):
    with open(fp, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    # Check sha
    sha = None
    r = requests.get(f"{API}/repos/{GH}/speakup/contents/{rel}", headers=H)
    if r.status_code == 200:
        sha = r.json().get("sha")

    payload = {"message": f"Add {rel}", "content": b64, "branch": "main"}
    if sha:
        payload["sha"] = sha

    r = requests.put(f"{API}/repos/{GH}/speakup/contents/{rel}", headers=H, json=payload)
    if r.status_code in (201, 200):
        ok += 1
    else:
        L(f"FAIL {rel}: {r.status_code}")

    if (i+1) % 20 == 0:
        L(f"  {ok}/{len(files)}")

# 写入结果
with open("upload_log.txt", "w", encoding="utf-8") as f:
    f.write(f"REPO: https://github.com/{GH}/speakup\n")
    f.write(f"OK: {ok}/{len(files)}\n")
    f.write("---\n")
    f.write("\n".join(log))
L(f"DONE: {ok}/{len(files)}")
