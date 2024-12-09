from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import WordBookmark, BookmarkWord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

def add_word_to_bookmark(user_id: int, word: str, meaning: str, example: str, db: Session):
    # 사용자가 등록한 단어가 100개를 초과했는지 확인
    count = db.query(WordBookmark).filter(WordBookmark.user_id == user_id).count()
    if count >= 100:
        raise HTTPException(status_code=400, detail="단어 북마크는 최대 100개까지 가능합니다.")

    # 사용자가 이미 동일한 단어를 등록했는지 확인
    existing_word = db.query(WordBookmark).filter(
        WordBookmark.user_id == user_id,
        WordBookmark.word == word
    ).first()
    if existing_word:
        raise HTTPException(status_code=400, detail="이미 북마크된 단어입니다.")

    # 새로운 단어를 데이터베이스에 추가
    new_word = WordBookmark(
        user_id=user_id,
        word=word,
        meaning=meaning,
        example=example
    )
    db.add(new_word)
    db.commit()
    db.refresh(new_word)  # 데이터베이스에서 새로 저장된 상태를 새로고침
    return new_word


async def delete_word_by_id(word_id: int, user_id: int, db: AsyncSession):
    """
    주어진 ID의 단어를 삭제합니다.
    """
    # 단어 조회
    result = await db.execute(select(BookmarkWord).filter_by(id=word_id, user_id=user_id))
    word = result.scalars().first()

    if not word:
        raise HTTPException(status_code=404, detail="Word not found or does not belong to the user.")

    # 단어 삭제
    await db.delete(word)
    await db.commit()
    return {"message": "Word deleted successfully."}

async def get_bookmark_words_by_user(user_id: int, db: AsyncSession) -> List[BookmarkWord]:
    """
    주어진 사용자 ID에 해당하는 단어장 목록을 조회합니다.
    """
    result = await db.execute(select(BookmarkWord).filter_by(user_id=user_id))
    words = result.scalars().all()
    return words

async def get_bookmark_words(user_id: int, db: AsyncSession):
    """
    사용자별 단어장 목록 조회
    """
    result = await db.execute(select(BookmarkWord).filter_by(user_id=user_id))
    words = result.scalars().all()
    return [
        {
            "id": word.id,
            "word": word.word,
            "definition": word.definition,
            "example": word.example,
        }
        for word in words
    ]

async def update_bookmark_word(word_id: int, user_id: int, update_data: dict, db: AsyncSession):
    """
    단어장에 등록된 단어를 수정합니다.
    """
    # 해당 단어 조회
    result = await db.execute(select(BookmarkWord).filter_by(id=word_id, user_id=user_id))
    word = result.scalars().first()

    if not word:
        raise HTTPException(status_code=404, detail="Word not found or does not belong to the user.")

    # 단어 정보 업데이트
    for key, value in update_data.items():
        if hasattr(word, key):
            setattr(word, key, value)

    await db.commit()
    await db.refresh(word)
    return {
        "id": word.id,
        "word": word.word,
        "definition": word.definition,
        "example": word.example,
    }