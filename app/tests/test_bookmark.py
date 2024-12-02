import pytest
from httpx import AsyncClient
from main import app
from app.database.db import get_db  # 실제 DB 세션 생성기
from models.models import User, BookmarkWord
from sqlalchemy import text


# DB 세션 fixture
@pytest.fixture(scope="function")
async def db():
    """
    실제 데이터베이스 세션 생성
    """
    async for session in get_db():
        yield session

# 테스트 데이터 정리 fixture
@pytest.fixture(scope="function", autouse=True)
async def cleanup_db(db):
    """
    테스트 종료 후 데이터 정리
    """
    yield
    await db.execute(text("TRUNCATE bookmark_words"))  # 테스트 데이터 삭제 # Truncate -> 1부터 다시 id 매겨줌 / 주의: 데이터 주의 - 캐시가 다 삭제됨
    await db.commit()

# 테스트 함수
@pytest.mark.asyncio
async def test_add_word_to_bookmark(db):
    """
    단어를 단어장에 성공적으로 추가
    """
# 테스트 사용자 추가
    test_user = User(kakao_id=123, password="apple1234", nickname="testuser", email="test@example.com")

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    test_bookmark = BookmarkWord(word="peach", user_id=test_user.id)

    db.add(test_bookmark)
    await db.commit()
    await db.refresh(test_bookmark)
    assert test_bookmark.word_id
    assert test_bookmark.user_id

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/bookmark/words",
            params={
                "user_id": test_user.id,
                "word": "example",
                "definition": "A representative form.",
                "example": "This is an example."
            }
        )
        # 응답 확인
        print(response.json())
        assert response.status_code == 200
        assert response.json()["message"] == "Word added to bookmark successfully."