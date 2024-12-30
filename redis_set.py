import redis
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()


def get_redis_client():
    """Redis 클라이언트 인스턴스를 반환"""
    # 환경 변수로 Redis 설정 불러오기
    redis_host = os.getenv("REDIS_HOST", "localhost")  # 기본값 'localhost'
    redis_port = int(os.getenv("REDIS_PORT", 6379))  # 기본값 6379
    redis_db = int(os.getenv("REDIS_DB", 0))  # 기본값 0

    try:
        # Redis 클라이언트 설정
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

        # Redis 서버에 ping을 보내서 연결 확인
        redis_client.ping()
        return redis_client

    except redis.ConnectionError as e:
        raise Exception(f"Redis connection error: {e}")