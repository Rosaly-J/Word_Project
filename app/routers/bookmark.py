from app.services.bookmark_service import get_bookmark_words_by_user, delete_word_by_id, update_bookmark_word
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import BookmarkWord, SearchHistory
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

@router.get("/")
async def list_bookmark_words(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 사용자 인증 및 ID 획득
):
    """
    사용자 단어장 목록 조회
    """
    return await get_bookmark_words(user_id=current_user["id"], db=db)

@router.patch("/{id}")
async def update_bookmark_word_route(
    id: int,
    update_data: dict,  # 수정할 데이터
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 사용자 인증 정보
):
    """
    사용자가 등록한 단어 정보 수정
    """
    try:
        return await update_bookmark_word(word_id=id, user_id=current_user["id"], update_data=update_data, db=db)
    except HTTPException as e:
        raise e

@router.delete("/bookmarks", response_model=dict)
async def delete_all_bookmark_words(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    사용자 단어장에 등록된 모든 단어 삭제
    """
    result = await db.execute(select(BookmarkWord).filter_by(user_id=current_user["id"]))
    bookmark_words = result.scalars().all()

    if not bookmark_words:
        raise HTTPException(status_code=404, detail="No bookmark words found")

    for word in bookmark_words:
        await db.delete(word)
    await db.commit()

    return {"message": "All bookmark words deleted successfully."}


@router.delete("/history/{id}", response_model=dict)
async def delete_search_history(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    특정 검색 기록 삭제
    """
    result = await db.execute(select(SearchHistory))
    search_history = result.scalars().all()
    print(search_history, "\n","\n","\n")

    if not search_history:
        raise HTTPException(status_code=404, detail="Search history not found")

    await db.delete(search_history)
    await db.commit()

    return {"message": f"Search history with ID {id} deleted successfully."}


@router.delete("/history", response_model=dict)
async def delete_all_search_histories(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    사용자 검색 기록 전체 삭제
    """
    result = await db.execute(select(SearchHistory).filter_by(user_id=current_user["id"]))
    search_histories = result.scalars().all()

    if not search_histories:
        raise HTTPException(status_code=404, detail="No search histories found")

    for history in search_histories:
        await db.delete(history)
    await db.commit()

    return {"message": "All search histories deleted successfully."}