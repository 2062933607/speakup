"""FastAPI 应用入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routers import characters, chat, speech

app = FastAPI(
    title="SpeakUp - English Speaking Practice",
    description="AI-powered English speaking practice with virtual characters",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由（必须在静态文件之前注册）
app.include_router(characters.router)
app.include_router(chat.router)
app.include_router(speech.router)

# 前端静态文件
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
_dist = FRONTEND_DIST

if _dist.exists():
    # 子目录直接挂载
    for sub in ["assets", "images", "fonts"]:
        sub_path = _dist / sub
        if sub_path.is_dir():
            app.mount(f"/{sub}", StaticFiles(directory=sub_path), name=f"static_{sub}")


def _serve_file(name: str):
    fp = _dist / name
    if fp.exists():
        return fp
    return None


@app.get("/sw.js")
async def sw():
    fp = _serve_file("sw.js")
    return FileResponse(fp) if fp else {"detail": "Not found"}


@app.get("/manifest.json")
async def manifest():
    fp = _serve_file("manifest.json")
    return FileResponse(fp) if fp else {"detail": "Not found"}


@app.get("/icon-192.png")
async def icon192():
    fp = _serve_file("icon-192.png")
    return FileResponse(fp) if fp else {"detail": "Not found"}


@app.get("/icon-512.png")
async def icon512():
    fp = _serve_file("icon-512.png")
    return FileResponse(fp) if fp else {"detail": "Not found"}


@app.get("/{full_path:path}")
async def spa_fallback(request: Request, full_path: str):
    """SPA 回退 — 所有非 API 路径返回 index.html"""
    # 已经是 API 路径的不走到这里
    fp = _dist / full_path
    if fp.exists() and fp.is_file():
        return FileResponse(fp)
    index = _dist / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend not built", "docs": "/docs"}


@app.get("/")
async def root():
    index = _dist / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "SpeakUp API is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    from backend.config import settings

    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
