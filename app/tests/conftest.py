import asyncio
import pytest
from app.database.db import AsyncSessionLocal
from sqlalchemy.future import select
from app.models.models import User
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(scope="function")
async def db() -> AsyncSession:
    """
    데이터베이스 세션 fixture
    """
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def create_test_user(db: AsyncSession):
    async def _create_user(kakao_id=123):
        """
        테스트용 사용자 생성
        """
        result = await db.execute(select(User).filter_by(kakao_id=kakao_id))
        existing_user = result.scalars().first()

        if existing_user:
            return existing_user

        test_user = User(
            kakao_id=kakao_id,
            email="test@example.com",
            nickname="testuser"
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        return test_user

    return _create_user

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

