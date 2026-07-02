"""虚拟人物模型"""
from pydantic import BaseModel
from typing import List, Optional


class Scenario(BaseModel):
    id: str
    name: str
    description: str
    opening_line: str
    expected_responses: List[str] = []


class Character(BaseModel):
    id: str
    name: str
    avatar: str  # emoji or image URL
    role: str
    accent: str  # 口音类型: american, british, australian
    personality: str
    system_prompt: str
    voice: str  # TTS voice name
    scenarios: List[Scenario] = []


class CharacterListItem(BaseModel):
    id: str
    name: str
    avatar: str
    role: str
    accent: str
    personality: str
    scenario_count: int


class CharacterListResponse(BaseModel):
    characters: List[CharacterListItem]
