import os

import redis
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # .env 파일을 로드하여 환경 변수를 읽어옴

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

class Settings(BaseSettings):
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "voca")

    # Redis 설정
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))

    # PostgreSQL DB URL 생성
    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis 연결 URL 생성
    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

# settings 인스턴스를 생성하여 사용할 수 있습니다.
settings = Settings()


# Redis 클라이언트 생성 함수

#     Redis 서버와 통신할 클라이언트를 생성.
#     - host, port, db 정보를 Settings 클래스에서 가져와서 초기화.

def get_redis_client():
    settings = Settings()
    return redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

# 예제 실행 코드 - 실행 전 redis 서버 실행
if __name__ == "__main__":
    settings = Settings()  # Settings 클래스 인스턴스 생성.

    # PostgreSQL 연결 URL 출력
    print("PostgreSQL URL:", settings.database_url)  # database_url 속성 값을 출력.

    # Redis 연결 URL 출력
    print("Redis URL:", settings.redis_url)  # redis_url 속성 값을 출력.

    # Redis 클라이언트를 생성하고, 키-값 저장 테스트
    redis_client = get_redis_client()  # Redis 클라이언트 생성.
    redis_client.set("test_key", "test_value")  # Redis에 "test_key"라는 키로 "test_value" 값을 저장.
    print("Redis test_key:", redis_client.get("test_key").decode("utf-8"))  # "test_key" 값을 가져와서 디코딩 후 출력.
