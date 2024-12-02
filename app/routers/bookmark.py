from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import BookmarkWord
from app.database.db import get_db
from pydantic import BaseModel


# Pydantic 모델 정의
class BookmarkWordCreate(BaseModel):
    word: str
    definition: str | None = None  # 선택적 필드
    example: str | None = None  # 선택적 필드

router = APIRouter()

@router.post("/bookmark/words")
async def add_word_to_bookmark(
    user_id: int,
    word: str,
    definition: str = None,
    example: str = None,
    db: AsyncSession = Depends(get_db)
):

    # 데이터 삽입
    new_word = BookmarkWord(
        user_id=user_id,  # user_id를 명시적으로 추가
        word=word,
        definition=definition,
        example=example,
        bookmark=True,
        study_category="VOCABULARY"
    )

    async with db.begin():
        db.add(new_word)
        await db.commit()

    return {"message": "Word added to bookmark successfully."}
