from fastapi import APIRouter, Query, HTTPException, Depends
import httpx
from app.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import SearchHistory, User
from sqlalchemy.future import select

router = APIRouter()

# dictionaryapi.dev를 호출하여 단어 정보 가져오기
async def get_word_info(word: str):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 404:  # 단어를 찾을 수 없는 경우
            raise HTTPException(status_code=404, detail="Word not found")

        if response.status_code != 200:  # 다른 에러 처리
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from dictionary API: {response.text}",
            )

        return response.json()

# word 엔드포인트 구현
@router.get("word")
async def search_word(word: str = Query(..., description="The word to search for")):
    word_info = await get_word_info(word)

    # 필요한 정보 추출 (예: 정의, 발음, 품사, 유의어, 예문 등)
    definitions = word_info[0].get("meanings", [])

    word_details = {
        "word": word,
        "definitions": [
            {
                "part_of_speech": meaning.get("partOfSpeech", "Unknown"),
                "definitions": meaning.get("definitions", []),
            }
            for meaning in definitions
        ],
        "pronunciation": word_info[0].get("phonetic", "No pronunciation available"),
        "synonyms": word_info[0]
        .get("meanings", [{}])[0]
        .get("synonyms", []),
        "example": word_info[0]
        .get("meanings", [{}])[0]
        .get("definitions", [{}])[0]
        .get("example", "No example available"),
    }

    return word_details

@router.get("history")
async def get_search_history(
    page: int = Query(1, ge=1),  # 페이지는 1 이상이어야 함
    page_size: int = Query(10, ge=1, le=100),  # 페이지 크기는 1 이상 100 이하
    db: AsyncSession = Depends(get_db),
):

    user_id = 1  # 인증 시스템과 연동 필요
    offset = (page - 1) * page_size

    # 검색 기록 쿼리
    query = select(SearchHistory).filter(SearchHistory.user_id == user_id).offset(offset).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    # 검색 기록이 없을 경우
    if not records:
        raise HTTPException(status_code=404, detail="No search history found")

    # 검색 기록을 JSON 직렬화 가능하도록 변환
    return {
        "records": [record.to_dict() for record in records]
    }