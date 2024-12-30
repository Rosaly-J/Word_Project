import asyncio
from unittest.mock import AsyncMock

import pytest
from app.database.db import AsyncSessionLocal
from sqlalchemy.future import select
from app.models.models import User
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncSession:
    """
    데이터베이스 세션 fixture
    """
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def create_test_user(db: AsyncSession):
    async def _create_user(kakao_id=123, id=1):
        """
        테스트용 사용자 생성
        """
        result = await db.execute(select(User).filter_by(id=id))
        existing_user = result.scalars().first()

        if existing_user:
            return existing_user

        test_user = User(
            kakao_id=kakao_id,
            id=id,
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

@pytest.fixture(scope="function", autouse=True)
def override_get_db():
    # Mock 세션 생성
    mock_session = AsyncMock()

    # get_db를 Mock으로 대체
    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.pop(get_db)
