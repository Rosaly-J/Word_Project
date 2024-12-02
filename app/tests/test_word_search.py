import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.models.models import Base, SearchHistory, User
from httpx import AsyncClient
from app.database.db import async_sessionmaker
from sqlalchemy import text

client = TestClient(app)

class TestWordSearch:
    client = TestClient(app)

    def test_search_word_valid(self):
        response = self.client.get("/search/word", params={"word": "example"})
        assert response.status_code == 200
        data = response.json()
        assert "word" in data
        assert "definitions" in data
        assert "pronunciation" in data
        assert "synonyms" in data
        assert "example" in data
        assert isinstance(data["definitions"], list)
        assert isinstance(data["synonyms"], list)

    def test_search_word_not_found(self):
        response = self.client.get("/search/word", params={"word": "nonexistentword"})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Word not found"

    def test_search_word_missing_param(self):
        response = self.client.get("/search/word")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "loc" in data["detail"][0]
        assert data["detail"][0]["loc"] == ["query", "word"]


# 비동기 데이터베이스 URL 설정
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://hwi:1234@localhost:5432/voca"

# 비동기 엔진 및 세션 생성
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# pytest의 이벤트 루프 설정
@pytest.fixture(scope="session")
def event_loop():
    """
    세션 범위의 이벤트 루프 설정
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# 데이터베이스 초기화
@pytest.fixture(scope="session", autouse=True)
async def init_db():
    """
    세션 범위의 데이터베이스 초기화
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # 테이블 생성
    yield
    async with engine.begin() as conn:
        # 테스트가 모두 끝난 뒤 실행
        await conn.run_sync(Base.metadata.drop_all)  # 모든 테이블 삭제

# 비동기 테스트 세션 생성
@pytest.fixture(scope="function")
async def test_db():
    """
    테스트용 비동기 데이터베이스 세션 생성
    """
    async with async_sessionmaker() as session:
        yield session

# 테스트 데이터 초기화 픽스처
@pytest.fixture(scope="function", autouse=True)
async def clear_test_data(test_db: AsyncSession):
    """
    테스트 실행 전 데이터베이스 초기화
    """
    async with test_db.begin():
        await test_db.execute(text("DELETE FROM search_history"))
        await test_db.execute(text("DELETE FROM users"))
        await test_db.commit()

# 테스트 데이터 추가
@pytest.fixture(scope="function")
async def setup_test_data(test_db: AsyncSession):
    """
    테스트 데이터를 DB에 추가
    """

    # 기존 데이터 확인
    async with test_db.begin():
        result = await test_db.execute(text("SELECT id FROM users WHERE id=1"))
        user_exists = result.scalar()

    # 데이터 삽입
    if not user_exists:
        async with test_db.begin():
            # 부모 테이블 데이터 추가
            test_db.add(User(
                id=1,
                kakao_id=12345,
                nickname="test_user",
                email="test@example.com",
                password="hashed_password"
            ))

            # 자식 테이블 데이터 추가
            test_db.add_all([
                SearchHistory(user_id=1, word="test_word_1"),
                SearchHistory(user_id=1, word="test_word_2"),
                SearchHistory(user_id=1, word="test_word_3"),
            ])


# 테스트 클래스
class TestSearchHistory:
    @pytest.mark.asyncio
    async def test_get_search_history_success(self, setup_test_data):
        """
        성공적으로 검색 기록 조회
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/search/history", params={"page": 1, "page_size": 2})

            # 응답 상태 코드 확인
            assert response.status_code == 200

            # JSON 데이터 확인
            data = response.json()["records"]
            print("반환된 데이터:", data)
            assert len(data) == 2  # 페이지 크기만큼 결과 반환
            assert data[0]["word"] == "test_word_1"  # 첫 번째 검색 기록
            assert data[1]["word"] == "test_word_2"  # 두 번째 검색 기록

    @pytest.mark.asyncio
    async def test_get_search_history_no_records(self):
        """
        검색 기록이 없을 때 404 반환
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/search/history")

            # 응답 상태 코드 확인
            assert response.status_code == 404
            assert response.json()["detail"] == "No search history found"

    @pytest.mark.asyncio
    async def test_get_search_history_pagination(self, setup_test_data):
        """
        페이지네이션 테스트
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/search/history", params={"page": 2, "page_size": 2})

            # 응답 상태 코드 확인
            assert response.status_code == 200

            # JSON 데이터 확인
            data = response.json()["records"]
            assert len(data) == 1  # 두 번째 페이지에는 1개만 남음
            assert data[0]["word"] == "test_word_3"  # 마지막 검색 기록
