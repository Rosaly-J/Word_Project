import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.database.db import get_db  # 실제 DB 세션 생성기
from models.models import User, BookmarkWord
from sqlalchemy import text
from sqlalchemy.future import select


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
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    test_bookmark = BookmarkWord(word="peach", user_id=test_user.id)

    db.add(test_bookmark)
    await db.commit()
    await db.refresh(test_bookmark)

    # 북마크 데이터 검증
    assert test_bookmark.id is not None
    assert test_bookmark.user_id == test_user.id

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/bookmark/words",
            json={
                "user_id": test_user.id,
                "word": "example",
                "definition": "A representative form.",
                "example": "This is an example."
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Word added to bookmark successfully."

@pytest.mark.asyncio
async def test_delete_word(db: AsyncSession):
    """
    단어 삭제 테스트
    """
    # 사용자 추가
    test_user = User(
        kakao_id=123, email="test@example.com", nickname="testuser", password="testpass"
    )
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # 단어 추가
    test_word = BookmarkWord(
        word="example",
        user_id=test_user.id
    )
    db.add(test_word)
    await db.commit()
    await db.refresh(test_word)

    # API 요청으로 단어 삭제
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/bookmark/words/{test_word.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Word deleted successfully."

        # 데이터베이스에서 단어 확인
        result = await db.execute(select(BookmarkWord).filter_by(id=test_word.id))
        deleted_word = result.scalars().first()
        assert deleted_word is None


@pytest.mark.asyncio
async def test_get_bookmark_words(db: AsyncSession):
    """
    단어장 목록 조회 테스트
    """
    # 테스트 사용자 추가
    test_user = User(
        kakao_id=123, email="test@example.com", nickname="testuser", password="testpass"
    )
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # 테스트 단어 추가
    words = [
        BookmarkWord(word="apple", definition="A fruit", example="I ate an apple.", user_id=test_user.id),
        BookmarkWord(word="banana", definition="A fruit", example="I like bananas.", user_id=test_user.id),
    ]
    db.add_all(words)
    await db.commit()

    # API 요청 테스트
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/bookmark/words", params={"user_id": test_user.id})
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2  # 단어 2개가 저장되어 있음
        assert data[0]["word"] == "apple"
        assert data[1]["word"] == "banana"

@pytest.mark.asyncio
async def test_list_bookmark_words(db: AsyncSession):
    """
    단어장 목록 조회 테스트
    """
    # 테스트 사용자 추가
    test_user = User(
        kakao_id=123, email="test@example.com", nickname="testuser", password="testpass"
    )
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # 테스트 단어 추가
    words = [
        BookmarkWord(word="apple", definition="A fruit", example="I ate an apple.", user_id=test_user.id),
        BookmarkWord(word="banana", definition="A fruit", example="I like bananas.", user_id=test_user.id),
    ]
    db.add_all(words)
    await db.commit()

    # API 요청 테스트
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/bookmark/words/",
            headers={"Authorization": "Bearer test_token"}  # 인증 헤더 추가
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2  # 단어 2개가 저장되어 있음
        assert data[0]["word"] == "apple"
        assert data[1]["word"] == "banana"

@pytest.mark.asyncio
async def test_update_bookmark_word(db: AsyncSession):
    """
    단어 정보 수정 테스트
    """
    # 테스트 사용자 추가
    test_user = User(
        kakao_id=123, email="test@example.com", nickname="testuser", password="testpass"
    )
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # 테스트 단어 추가
    test_word = BookmarkWord(
        word="apple",
        definition="A fruit",
        example="I like apples.",
        user_id=test_user.id
    )
    db.add(test_word)
    await db.commit()
    await db.refresh(test_word)

    # 수정 요청 데이터
    update_data = {
        "definition": "A common fruit",
        "example": "Apples are red and sweet."
    }

    # API 요청 테스트
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch(
            f"/bookmark/words/{test_word.id}",
            json=update_data,
            headers={"Authorization": "Bearer test_token"}  # 인증 헤더 추가
        )
        assert response.status_code == 200

        updated_word = response.json()
        assert updated_word["definition"] == update_data["definition"]
        assert updated_word["example"] == update_data["example"]

        # 데이터베이스에서 확인
        result = await db.execute(select(BookmarkWord).filter_by(id=test_word.id))
        word = result.scalars().first()
        assert word.definition == update_data["definition"]
        assert word.example == update_data["example"]

@pytest.mark.asyncio
async def test_delete_all_bookmark_words(db: AsyncSession):
    """
    단어장 전체 삭제 테스트
    """
    # 테스트 사용자 추가
    test_user = User(
        kakao_id=123, email="test@example.com", nickname="testuser", password="testpass"
    )
    result = await db.execute(select(User).filter_by(kakao_id=123))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user  # 이미 존재하면 기존 사용자 반환

    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # 테스트 단어 추가
    words = [
        BookmarkWord(word="apple", definition="A fruit", example="I ate an apple.", user_id=test_user.id),
        BookmarkWord(word="banana", definition="A fruit", example="I like bananas.", user_id=test_user.id),
    ]
    db.add_all(words)
    await db.commit()

    # 삭제 API 호출
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            "/bookmark/words",
            headers={"Authorization": "Bearer test_token"}  # 인증 헤더 추가
        )
        assert response.status_code == 200
        assert response.json()["message"] == "All bookmark words deleted successfully."

        # 데이터베이스에서 확인
        result = await db.execute(select(BookmarkWord).filter_by(user_id=test_user.id))
        remaining_words = result.scalars().all()
        assert len(remaining_words) == 0  # 모든 단어가 삭제되었는지 확인

# 코드 리펙토링 가능한지 -> 중복 되는 코드 (테스트 사용자 한번만 사용하고 class로 묶을 수 있는지)