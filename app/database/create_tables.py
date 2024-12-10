import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.models import Base

# 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://hwi:1234@localhost:5432/voca"

# 비동기 엔진 생성
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

async def create_tables():
    """
    데이터베이스에 테이블 생성
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("테이블이 생성되었습니다.")

if __name__ == "__main__":
    asyncio.run(create_tables())
