import pytest
from fastapi.testclient import TestClient
from main import app  # FastAPI 앱을 임포트합니다

client = TestClient(app)

class TestWordSearchBar:

    # 테스트 케이스 1: 유효한 단어에 대한 자동 완성 제안
    def test_suggest_word_valid(self):
        response = client.post("/search/suggest", json={"query": "ap"})
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert "apple" in data["suggestions"]
        assert "application" in data["suggestions"]

    # 테스트 케이스 2: 유효한 단어에 대해 제안이 없는 경우
    def test_suggest_word_no_suggestions(self):
        response = client.post("/search/suggest", json={"query": "xyz"})
        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []

    # 테스트 케이스 3: 입력값이 숫자인 경우
    def test_suggest_word_with_numbers(self):
        response = client.post("/search/suggest", json={"query": "apple123"})
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["msg"] == "String should match pattern '^[a-zA-Z]+$'"

    # 테스트 케이스 4: 입력값에 특수문자가 포함된 경우
    def test_suggest_word_with_special_characters(self):
        response = client.post("/search/suggest", json={"query": "app!le"})
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["msg"] == "String should match pattern '^[a-zA-Z]+$'"

    # 테스트 케이스 5: 최소 글자 수 1자 이상 확인
    def test_suggest_word_min_length(self):
        response = client.post("/search/suggest", json={"query": ""})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "String should have at least 1 character" in data["detail"][0]["msg"]

