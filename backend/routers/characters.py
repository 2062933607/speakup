"""人物 & 场景 API 路由"""
import json
from pathlib import Path
from fastapi import APIRouter

from backend.models.character import Character, CharacterListItem, CharacterListResponse, Scenario

router = APIRouter(prefix="/api", tags=["characters"])

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_characters() -> list[dict]:
    with open(DATA_DIR / "characters.json", "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/characters", response_model=CharacterListResponse)
async def list_characters():
    """获取虚拟人物列表"""
    chars = _load_characters()
    items = [
        CharacterListItem(
            id=c["id"],
            name=c["name"],
            avatar=c["avatar"],
            role=c["role"],
            accent=c["accent"],
            personality=c["personality"],
            scenario_count=len(c.get("scenarios", [])),
        )
        for c in chars
    ]
    return CharacterListResponse(characters=items)


@router.get("/characters/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """获取虚拟人物详情（包含场景）"""
    chars = _load_characters()
    for c in chars:
        if c["id"] == character_id:
            return Character(**c)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Character not found")


@router.get("/scenarios")
async def list_scenarios(character_id: str | None = None):
    """获取场景列表，可按人物筛选"""
    chars = _load_characters()
    all_scenarios = []
    for c in chars:
        if character_id and c["id"] != character_id:
            continue
        for s in c.get("scenarios", []):
            all_scenarios.append({
                **s,
                "character_id": c["id"],
                "character_name": c["name"],
            })
    return {"scenarios": all_scenarios}
