from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List

router = APIRouter()

# 과거 검색 기록 (예제 데이터를 위한 임시 저장소)
search_history = ["apple", "application", "banana", "band", "cat", "dog"]

# 입력 데이터 모델
class SuggestRequest(BaseModel):
    query: str = Field(..., min_length=1, pattern="^[a-zA-Z]+$")  # 'regex' 대신 'pattern' 사용

# 출력 데이터 모델
class SuggestResponse(BaseModel):
    suggestions: List[str]

# /search/suggest 엔드포인트 구현
@router.post("/search/suggest", response_model=SuggestResponse)
async def suggest_words(request: SuggestRequest = Body(...)):
    query = request.query.lower()

    # 과거 검색 기록에서 자동 완성 제안
    suggestions = [word for word in search_history if word.startswith(query)]

    # 제안이 없으면 빈 배열 반환
    return {"suggestions": suggestions}

