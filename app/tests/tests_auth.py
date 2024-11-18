import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def kakao_mock_response(mocker):
    # Kakao API를 모킹하여 테스트
    mocker.patch("app.services.kakao_oauth.KakaoOAuthService.get_access_token", return_value="mock_access_token")
    mocker.patch("app.services.kakao_oauth.KakaoOAuthService.get_user_info", return_value={
        "id": 123456789,
        "kakao_account": {"email": "testuser@kakao.com"},
        "properties": {"nickname": "TestUser"}
    })

def test_kakao_login():
    response = client.get("/auth/kakao/login")
    assert response.status_code == 200
    assert "login_url" in response.json()

def test_kakao_callback(kakao_mock_response):
    # 카카오 OAuth callback 테스트
    response = client.get("/auth/kakao/callback", params={"code": "mock_code"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "access_token" in data
