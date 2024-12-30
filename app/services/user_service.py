from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, SearchHistory
from typing import List, Dict
import bcrypt

async def get_user_by_kakao_id(db: AsyncSession, kakao_id: str):
    """카카오 ID로 사용자 조회 (비동기)"""
    result = await db.execute(select(User).where(User.kakao_id == kakao_id))
    user = result.scalar_one_or_none()  # 조회된 사용자 반환 (없으면 None)
    return user

async def create_user(db: AsyncSession, user_data: dict):
    """사용자 생성 (비동기)"""
    # 소셜 로그인의 경우 비밀번호가 없을 수 있음
    if "password" in user_data and user_data["password"]:
        # 비밀번호가 있으면 해시화
        hashed_password = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_data["password"] = hashed_password
    else:
        # 소셜 로그인에서는 비밀번호 없음
        user_data["password"] = ""  # 비밀번호가 없으면 빈 문자열로 처리

    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()  # 비동기 커밋
    await db.refresh(new_user)  # 새로 생성된 사용자 데이터 갱신
    return new_user

async def get_search_history(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
) -> List[Dict]:
    """
    사용자의 검색 기록을 페이지네이션하여 가져옵니다.
    """
    # 검색 기록 쿼리 작성
    query = select(SearchHistory).filter(SearchHistory.user_id == user_id)
    query = query.limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    # 결과 반환
    return [{"id": record.id, "word": record.word, "created_at": record.created_at} for record in records]