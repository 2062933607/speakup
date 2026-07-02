"""语音相关 API 路由"""
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response

from backend.services.stt_service import speech_to_text
from backend.services.tts_service import text_to_speech
from backend.services.pronunciation_service import score_pronunciation

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/stt")
async def stt(audio: UploadFile = File(...)):
    """语音转文字"""
    audio_data = await audio.read()
    audio_format = audio.filename.split(".")[-1] if audio.filename else "webm"
    text = await speech_to_text(audio_data, audio_format)
    return {"text": text}


@router.post("/tts")
async def tts(
    text: str = Form(...),
    voice: str = Form("american_female"),
):
    """文字转语音"""
    audio = await text_to_speech(text, voice)
    return Response(content=audio, media_type="audio/mpeg")


@router.post("/pronunciation/score")
async def pronunciation_score(
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
):
    """发音评分"""
    audio_data = await audio.read()
    audio_format = audio.filename.split(".")[-1] if audio.filename else "webm"
    recognized_text = await speech_to_text(audio_data, audio_format)
    result = score_pronunciation(expected_text, recognized_text)
    return result
