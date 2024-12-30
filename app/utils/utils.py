import jwt
from datetime import datetime, timedelta
import redis
from dotenv import load_dotenv
import os
from fastapi import HTTPException
from redis_set import get_redis_client

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"

def create_jwt_token(data: dict):
    """JWT 토큰 생성"""
    expire = datetime.utcnow() + timedelta(days=1)  # 1일 유효기간
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """JWT 리프레시 토큰 생성"""
    expire = datetime.utcnow() + timedelta(days=30)  # 30일 유효기간
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def delete_access_token(token: str):
    """Redis에서 엑세스 토큰 삭제"""
    try:

        redis_client = get_redis_client()  # Redis 클라이언트 가져오기
        result = redis_client.delete(f"access_token:{token}")

        if result == 0:
            # 유효하지 않은 토큰에 대해 401 응답
            raise HTTPException(status_code=401, detail="Invalid token")  # 401 상태 코드로 변경

        return {"message": "Logout successful"}

    except redis.exceptions.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except HTTPException as e:
        raise e  # 이 예외는 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def delete_refresh_token(user_id: str):
    """Redis에서 리프레시 토큰 삭제"""
    try:
        redis_client = get_redis_client()  # Redis 클라이언트 가져오기
        result = redis_client.delete(f"refresh_token:{user_id}")

        if result == 0:
            # 유효하지 않은 리프레시 토큰에 대해 401 응답
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        return {"message": "Refresh token deleted successfully"}

    except redis.exceptions.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def verify_refresh_token(refresh_token: str):
    """리프레시 토큰 검증"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")