"""对话模型"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    role: str  # user 或 assistant
    text: str
    audio_url: Optional[str] = None
    pronunciation_score: Optional[dict] = None
    timestamp: datetime = datetime.now()


class Conversation(BaseModel):
    id: str
    character_id: str
    scenario_id: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = datetime.now()


class SendMessageRequest(BaseModel):
    conversation_id: str
    text: str


class SendVoiceRequest(BaseModel):
    conversation_id: str
    expected_text: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    user_message: Message
    assistant_message: Message
