import pytest
from fastapi.testclient import TestClient
from main import app
from utils.utils import create_jwt_token, get_redis_client

client = TestClient(app)

@pytest.fixture
def kakao_mock_response(mocker):
    # Kakao API를 모킹하여 테스트
    mocker.patch("app.services.kakao_oauth.KakaoOAuthService.get_access_token", new_callble=mocker.AsyncMock, return_value="mock_access_token")
    mocker.patch("app.services.kakao_oauth.KakaoOAuthService.get_user_info", new_callble=mocker.AsyncMock, return_value={
        "id": 123456789,
        "kakao_account": {"email": "testuser@kakao.com"},
        "properties": {"nickname": "TestUser"},
        "password": "securepassword123"
    })
@pytest.fixture
def valid_jwt_token():
    # 테스트를 위한 유효한 JWT 토큰 발급
    user_data = {"user_id": 1, "kakao_id": 123456}
    return create_jwt_token(user_data)  # create_jwt_token은 실제 토큰 발급 함수

@pytest.fixture
def redis_setup():
    """테스트용 Redis 클라이언트 설정 및 초기화"""
    redis_client = get_redis_client()  # Redis 클라이언트를 가져옴
    redis_client.flushdb()  # 테스트 전 Redis DB 초기화
    yield redis_client
    redis_client.flushdb()  # 테스트 후 Redis DB 초기화

def test_kakao_login():
    response = client.get("/auth/kakao", params={"code": "mock_code"})
    assert response.status_code == 200
    assert "login_url" in response.json()

def test_kakao_callback(kakao_mock_response):
    response = client.get("/auth/kakao/callback", params={"code": "mock_code"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "access_token" in data


class TestLogout:
    def test_logout_valid_token(self, redis_setup, valid_jwt_token):
        """유효한 토큰으로 로그아웃"""
        # 리프레시 토큰을 Redis에 저장
        redis_setup.set(f"access_token:{valid_jwt_token}", "mock_value")

        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # 응답 코드가 200 OK인지 확인
        assert response.status_code == 200
        assert response.json() == {"message": "Logout successful"}

        # Redis에서 액세스 토큰이 삭제되었는지 확인
        token_exists = redis_setup.exists(f"access_token:{valid_jwt_token}")
        assert not token_exists  # 리프레시 토큰이 삭제되었어야 함

    def test_logout_invalid_token(self, redis_setup):
        """유효하지 않은 토큰으로 로그아웃 시도"""
        invalid_token = "invalid_token_string"

        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        # 응답 코드가 401 Unauthorized인지 확인
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}

    def test_logout_missing_token(self):
        """토큰이 없을 때 로그아웃 시도"""
        response = client.post("/auth/logout")

        # 응답 코드가 401 Unauthorized인지 확인
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

