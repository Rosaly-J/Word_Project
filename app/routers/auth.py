from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.kakao_oauth import KakaoOAuthService, get_kakao_service
from app.services.user_service import create_user
from app.database.db import get_db  # SQLAlchemy 세션 가져오는 함수
from app.utils.utils import create_jwt_token, delete_access_token, create_refresh_token, \
    verify_refresh_token  # JWT 발급 함수
from app.models.models import User
import redis.asyncio as redis
router = APIRouter()

# Redis 비동기 클라이언트 설정
async def get_redis_client():
    client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    return client

# 카카오 로그인 URL 반환
@router.get("/auth/kakao")
async def kakao_login(service: KakaoOAuthService = Depends(get_kakao_service)):
    login_url = service.get_login_url()
    return {"login_url": login_url}

# 카카오 인증 후 콜백 처리
@router.get("/auth/kakao/callback")
async def kakao_callback(
    code: str = Query(...),
    service: KakaoOAuthService = Depends(get_kakao_service),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Access Token 발급
        print(f"Received code: {code}")
        print(f"Service: {service}")
        access_token = await service.get_access_token(code)

        # 사용자 정보 가져오기
        user_info = await service.get_user_info(access_token)
        kakao_id = user_info["id"]
        email = user_info["kakao_account"]["email"]
        nickname = user_info.get("properties", {}).get("nickname")

        # 데이터베이스에서 사용자 조회
        query = select(User).filter(User.kakao_id == kakao_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # 신규 사용자면 회원가입 처리
            user_data = {
                "kakao_id": kakao_id,
                "email": email,
                "nickname": nickname,
                "password": None,
            }
            user = await create_user(db, user_data)

        # 액세스 토큰 및 리프레시 토큰 발급
        access_token = create_jwt_token({"user_id": user.id, "kakao_id": user.kakao_id})
        refresh_token = create_refresh_token({"user_id": user.id, "kakao_id": user.kakao_id})

        # Redis 클라이언트 비동기적으로 가져오기
        redis_client = await get_redis_client()

        # 리프레시 토큰을 Redis에 저장 (만료 기간 설정)
        await redis_client.setex(f"refresh_token:{user.id}", 3600 * 24 * 30, refresh_token)  # 30일 동안 유효

        # 로그인 성공 메시지와 access_token 반환
        return {"message": "Login successful", "access_token": access_token}


    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in user info: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # 예외 메시지 출력
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 리프레시 토큰을 통해 새로운 액세스 토큰 발급
@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """리프레시 토큰을 통해 액세스 토큰 재발급"""
    try:
        # 리프레시 토큰 검증
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        # 새로운 액세스 토큰 발급
        access_token = create_jwt_token({"user_id": user_id})

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/logout")
async def logout(authorization: str = Header(None)):
    """로그아웃: Redis에서 엑세스 토큰 삭제"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Bearer 토큰 추출
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # 토큰 삭제
    return delete_access_token(token)