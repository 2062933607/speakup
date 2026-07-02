"""对话 API 路由"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.services.llm_service import chat
from backend.services.stt_service import speech_to_text
from backend.services.tts_service import text_to_speech
from backend.services.pronunciation_service import score_pronunciation
from backend.routers.characters import _load_characters
from backend.models.conversation import (
    SendMessageRequest,
    ChatResponse,
    Message,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 简易内存存储（生产环境应使用数据库）
conversations: dict[str, dict] = {}


def _get_character(character_id: str) -> dict | None:
    chars = _load_characters()
    for c in chars:
        if c["id"] == character_id:
            return c
    return None


def _get_scenario(character: dict, scenario_id: str | None) -> dict | None:
    if not scenario_id:
        return None
    for s in character.get("scenarios", []):
        if s["id"] == scenario_id:
            return s
    return None


def _create_conversation(character_id: str, scenario_id: str | None = None) -> dict:
    conv_id = str(uuid.uuid4())
    conversations[conv_id] = {
        "id": conv_id,
        "character_id": character_id,
        "scenario_id": scenario_id,
        "messages": [],
        "created_at": datetime.now().isoformat(),
    }
    return conversations[conv_id]


@router.post("/start")
async def start_conversation(character_id: str, scenario_id: str | None = None):
    """开始新对话，返回开场白"""
    character = _get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    conv = _create_conversation(character_id, scenario_id)

    scenario = _get_scenario(character, scenario_id)
    opening = scenario["opening_line"] if scenario else f"Hi! I'm {character['name']}. Nice to meet you! How are you today?"

    # 生成开场白语音（TTS 失败不影响对话开始）
    audio_base64 = None
    try:
        audio = await text_to_speech(opening, character["voice"])
        if audio:
            import base64
            audio_base64 = base64.b64encode(audio).decode("utf-8")
    except Exception:
        pass

    msg = {
        "role": "assistant",
        "text": opening,
        "audio_base64": audio_base64,
        "timestamp": datetime.now().isoformat(),
    }
    conv["messages"].append(msg)

    return {
        "conversation_id": conv["id"],
        "message": msg,
        "has_audio": audio_base64 is not None,
    }


@router.post("/send", response_model=ChatResponse)
async def send_message(req: SendMessageRequest):
    """发送文字消息"""
    conv = conversations.get(req.conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    character = _get_character(conv["character_id"])
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 保存用户消息
    user_msg = {
        "role": "user",
        "text": req.text,
        "timestamp": datetime.now().isoformat(),
    }
    conv["messages"].append(user_msg)

    # 构建 LLM 消息历史
    llm_messages = [
        {"role": m["role"], "content": m["text"]}
        for m in conv["messages"][:-1]
    ]

    # 获取 LLM 回复
    reply = await chat(character["system_prompt"], llm_messages, req.text)

    # 保存助手消息
    assistant_msg = {
        "role": "assistant",
        "text": reply,
        "timestamp": datetime.now().isoformat(),
    }
    conv["messages"].append(assistant_msg)

    return ChatResponse(
        conversation_id=conv["id"],
        user_message=Message(**user_msg),
        assistant_message=Message(**assistant_msg),
    )


@router.post("/send-voice")
async def send_voice(
    conversation_id: str = Form(...),
    audio: UploadFile = File(...),
    expected_text: str | None = Form(None),
):
    """发送语音消息"""
    conv = conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    character = _get_character(conv["character_id"])
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 读取音频数据
    audio_data = await audio.read()
    audio_format = audio.filename.split(".")[-1] if audio.filename else "webm"

    # STT 识别
    recognized_text = await speech_to_text(audio_data, audio_format)

    # 如果 STT 返回错误占位符，不发送给 LLM，直接返回提示
    is_stt_error = recognized_text.startswith("[")
    if is_stt_error:
        user_msg = {
            "role": "user",
            "text": recognized_text,
            "timestamp": datetime.now().isoformat(),
        }
        conv["messages"].append(user_msg)
        assistant_msg = {
            "role": "assistant",
            "text": "I'm sorry, I couldn't hear that clearly. Could you try again or type your message?",
            "timestamp": datetime.now().isoformat(),
        }
        conv["messages"].append(assistant_msg)
        return {
            "conversation_id": conv["id"],
            "user_message": user_msg,
            "assistant_message": assistant_msg,
        }

    # 发音评分
    pronunciation = None
    if expected_text:
        pronunciation = score_pronunciation(expected_text, recognized_text)

    # 保存用户消息
    user_msg = {
        "role": "user",
        "text": recognized_text,
        "pronunciation_score": pronunciation,
        "timestamp": datetime.now().isoformat(),
    }
    conv["messages"].append(user_msg)

    # 构建 LLM 消息历史
    llm_messages = [
        {"role": m["role"], "content": m["text"]}
        for m in conv["messages"][:-1]
    ]

    # 获取 LLM 回复
    reply = await chat(character["system_prompt"], llm_messages, recognized_text)

    # TTS 合成（失败不影响对话）
    audio_base64 = None
    try:
        audio_response = await text_to_speech(reply, character["voice"])
        if audio_response:
            import base64
            audio_base64 = base64.b64encode(audio_response).decode("utf-8")
    except Exception:
        pass

    # 保存助手消息
    assistant_msg = {
        "role": "assistant",
        "text": reply,
        "audio_base64": audio_base64,
        "timestamp": datetime.now().isoformat(),
    }
    conv["messages"].append(assistant_msg)

    return {
        "conversation_id": conv["id"],
        "user_message": {
            **user_msg,
            "pronunciation_score": pronunciation,
        },
        "assistant_message": {
            **assistant_msg,
        },
    }


@router.get("/conversations")
async def list_conversations():
    """获取历史对话列表"""
    return {
        "conversations": [
            {
                "id": c["id"],
                "character_id": c["character_id"],
                "scenario_id": c["scenario_id"],
                "message_count": len(c["messages"]),
                "created_at": c["created_at"],
                "preview": c["messages"][0]["text"][:50] if c["messages"] else "",
            }
            for c in conversations.values()
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取单个对话详情"""
    conv = conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/tts/{conversation_id}/{message_index}")
async def get_tts_audio(conversation_id: str, message_index: int):
    """获取指定消息的 TTS 音频"""
    from fastapi.responses import Response

    conv = conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if message_index >= len(conv["messages"]):
        raise HTTPException(status_code=404, detail="Message not found")

    msg = conv["messages"][message_index]
    if msg["role"] != "assistant":
        raise HTTPException(status_code=400, detail="Only assistant messages have audio")

    character = _get_character(conv["character_id"])
    audio = await text_to_speech(msg["text"], character["voice"])

    return Response(content=audio, media_type="audio/mpeg")
