"""语音相关 API 路由 — 手动解析 multipart，避免依赖 python-multipart"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response

from backend.services.stt_service import speech_to_text
from backend.services.tts_service import text_to_speech
from backend.services.pronunciation_service import score_pronunciation

router = APIRouter(prefix="/api/speech", tags=["speech"])


def _get_param(header: str, param: str) -> str | None:
    for part in header.split(";"):
        part = part.strip()
        if part.startswith(param + "="):
            val = part.split("=", 1)[1].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            return val
    return None


def _parse(body: bytes, boundary: bytes) -> list[tuple[str, dict, bytes]]:
    parts = []
    sep = b"--" + boundary
    for section in body.split(sep)[1:-1]:
        section = section.lstrip(b"\r\n")
        if b"\r\n\r\n" not in section:
            continue
        hdr, content = section.split(b"\r\n\r\n", 1)
        content = content.rstrip(b"\r\n")
        if content.endswith(b"\r\n"):
            content = content[:-2]
        disp = ""
        headers = {}
        for line in hdr.split(b"\r\n"):
            s = line.decode("utf-8", errors="ignore")
            if s.lower().startswith("content-disposition"):
                disp = s
            elif ":" in s:
                k, v = s.split(":", 1)
                headers[k.strip()] = v.strip()
        parts.append((disp, headers, content))
    return parts


async def _parse_multipart(request: Request) -> dict[str, tuple[str, bytes]]:
    body = await request.body()
    ct = request.headers.get("content-type", "")
    boundary = ct.split("boundary=")[-1].strip().strip('"')
    result = {}
    for disp, _, content in _parse(body, boundary.encode()):
        name = _get_param(disp, "name")
        filename = _get_param(disp, "filename")
        if name:
            result[name] = (filename or "", content)
    return result


@router.post("/stt")
async def stt(request: Request):
    """语音转文字"""
    parts = await _parse_multipart(request)
    audio_part = parts.get("audio")
    if not audio_part:
        raise HTTPException(400, "Missing 'audio' field")
    filename, audio_data = audio_part
    fmt = filename.split(".")[-1] if filename else "webm"
    text = await speech_to_text(audio_data, fmt)
    return {"text": text}


@router.post("/tts")
async def tts(request: Request):
    """文字转语音"""
    parts = await _parse_multipart(request)
    text_part = parts.get("text")
    voice_part = parts.get("voice")
    if not text_part:
        raise HTTPException(400, "Missing 'text' field")
    text = text_part[1].decode("utf-8")
    voice = voice_part[1].decode("utf-8") if voice_part else "american_female"
    audio = await text_to_speech(text, voice)
    return Response(content=audio, media_type="audio/mpeg")


@router.post("/pronunciation/score")
async def pronunciation_score(request: Request):
    """发音评分"""
    parts = await _parse_multipart(request)
    text_part = parts.get("expected_text")
    audio_part = parts.get("audio")
    if not text_part or not audio_part:
        raise HTTPException(400, "Missing 'expected_text' or 'audio'")
    expected_text = text_part[1].decode("utf-8")
    _, audio_data = audio_part
    recognized = await speech_to_text(audio_data, "webm")
    result = score_pronunciation(expected_text, recognized)
    return result
