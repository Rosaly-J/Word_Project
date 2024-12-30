import os
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.database.db import get_db
import jwt
from sqlalchemy import select

from app.schemas.oauth import oauth2_scheme

# 시크릿 키 및 알고리즘
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"

async def get_current_user(
    token: str = Depends(oauth2_scheme),  # 클라이언트에서 제공한 토큰
    db: AsyncSession = Depends(get_db)   # DB 연결
) -> User:

    # 테스트용 토큰 처리
    if token == "test_token":
        # 테스트용 사용자 생성 및 반환
        user = User(kakao_id=123, id=1, email="test@example.com", nickname="testuser")
        return user  # 테스트 사용자 반환

    try:
        # JWT 디코드 및 유효성 검사
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # 사용자 조회
        query = await db.execute(select(User).filter(User.id == user_id))
        user = query.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

