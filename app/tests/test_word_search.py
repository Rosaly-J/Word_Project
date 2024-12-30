import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.models.models import Base, SearchHistory, User
from httpx import AsyncClient
from app.database.db import AsyncSessionLocal
from sqlalchemy import text, select
from dependencies import get_db

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

# 비동기 테스트 세션 생성
@pytest.fixture(scope="function")
async def test_db():
    """
    테스트용 비동기 데이터베이스 세션 생성
    """
    async with AsyncSessionLocal() as session:
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
@pytest.mark.asyncio
class TestSearchHistory:

    async def test_get_search_history_success(self, setup_test_data):
        """
        성공적으로 검색 기록 조회
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/search/history/", params={"page": 1, "page_size": 2})

            # 응답 상태 코드 확인
            assert response.status_code == 200

            # JSON 데이터 확인
            data = response.json()["records"]
            assert len(data) == 2  # 페이지 크기만큼 결과 반환
            assert data[0]["word"] == "test_word_1"  # 첫 번째 검색 기록
            assert data[1]["word"] == "test_word_2"  # 두 번째 검색 기록


    async def test_get_search_history_no_records(self):
        """
        검색 기록이 없을 때 404 반환
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/search/history")

            # 응답 상태 코드 확인
            assert response.status_code == 404
            assert response.json()["detail"] == "No search history found"


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

@pytest.mark.asyncio
class TestSearchHistory:
    """
    검색 기록 삭제 테스트 클래스
    """
    async def create_test_user(self, db: AsyncSession, kakao_id=123):
        """
        테스트 사용자를 생성하거나 반환
        """
        result = await db.execute(select(User).filter_by(kakao_id=kakao_id))
        existing_user = result.scalars().first()

        if existing_user:
            return existing_user  # 이미 존재하면 기존 사용자 반환

        test_user = User(
            kakao_id=kakao_id,
            email="test@example.com",
            nickname="testuser"
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        return test_user

    async def test_delete_single_search_history(self, client: AsyncClient, db: AsyncSession, create_test_user):
        """
        특정 검색 기록 삭제 테스트
        """
        # 테스트 사용자 생성
        test_user = await create_test_user()

        # 검색 기록 추가
        test_history = SearchHistory(user_id=test_user.id, word="default_word")
        db.add(test_history)
        await db.commit()
        await db.refresh(test_history)

        # 단일 삭제 API 호출
        response = await client.delete(
            f"/search/history/{test_history.id}",
            headers={"Authorization": "Bearer test_token"},
        )
        print(test_history.id)
        print(test_user.id)
        print(response)

        # 응답 검증
        assert response.status_code == 200
        assert response.json()["message"] == f"Search history with ID {test_history.id} deleted successfully."

    async def test_delete_all_search_history(self, client: AsyncClient, db: AsyncSession, create_test_user):
        """
        사용자 검색 기록 전체 삭제 테스트
        """
        # 테스트 사용자 생성
        test_user = await create_test_user()

        # 검색 기록 추가
        histories = [
            SearchHistory(user_id=test_user.id, word="word1"),
            SearchHistory(user_id=test_user.id, word="word2"),
        ]
        db.add_all(histories)
        await db.commit()

        # 생성된 기록 수 확인
        result = await db.execute(select(SearchHistory).filter_by(user_id=test_user.id))
        initial_histories = result.scalars().all()
        assert len(initial_histories) == 2
        print("!!!!!")
        print(initial_histories)

        # 전체 삭제 API 호출
        response = await client.delete(
            "/remove",
            headers={"Authorization": "Bearer test_token"},
        )

        # 응답 검증
        assert response.status_code == 200
        assert response.json()["message"] == "All search history deleted successfully."

        # 데이터베이스 상태 검증
        result = await db.execute(select(SearchHistory).filter_by(user_id=test_user.id))
        remaining_histories = result.scalars().all()
        assert len(remaining_histories) == 0
