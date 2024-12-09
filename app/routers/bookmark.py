
from app.services.bookmark_service import get_bookmark_words_by_user, delete_word_by_id
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import BookmarkWord
from app.database.db import get_db
from pydantic import BaseModel

from dependencies import get_current_user


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

router = APIRouter(prefix="/bookmark/words", tags=["Bookmark"])

@router.get("/")
async def get_bookmark_words(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 사용자 인증 및 ID 획득
):
    """
    사용자 단어장 목록 조회
    """
    return await get_bookmark_words_by_user(user_id=current_user["id"], db=db)

@router.delete("/{id}")
async def delete_bookmark_word(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 사용자 인증 정보
):
    """
    사용자가 등록한 단어 삭제
    """
    try:
        return await delete_word_by_id(word_id=id, user_id=current_user["id"], db=db)
    except HTTPException as e:
        raise e