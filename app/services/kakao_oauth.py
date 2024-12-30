import httpx
import os
from dotenv import load_dotenv

load_dotenv()

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"


class KakaoOAuthService:
    def __init__(self, client_id: str, redirect_uri: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def get_login_url(self) -> str:
        """카카오 로그인 URL 생성"""
        url = f"https://kauth.kakao.com/oauth/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code"
        return url

    async def get_access_token(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                # Kakao에서 access token 요청
                response = await client.post(
                    KAKAO_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "redirect_uri": self.redirect_uri,
                        "code": code,
                    },
                )
                response.raise_for_status()  # HTTP 상태 코드 확인

                # 응답에서 access_token 추출
                access_token = response.json().get("access_token")
                if not access_token:
                    raise ValueError("Access token not found in the response.")

                return access_token

            except httpx.HTTPStatusError as e:
                print(f"HTTP request failed: {e}")
                raise e
            except ValueError as e:
                print(f"Value error: {e}")
                raise e
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise e

    async def get_user_info(self, access_token: str):
        async with httpx.AsyncClient() as client:
            try:
                # Kakao에서 사용자 정보 요청
                response = await client.get(
                    KAKAO_USER_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()  # HTTP 상태 코드 확인

                # 사용자 정보 반환
                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"HTTP request failed: {e}")
                raise e
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise e


# 환경 변수에서 Kakao client_id와 redirect_uri를 가져오는 방법

def get_kakao_service() -> KakaoOAuthService:
    client_id = os.getenv("KAKAO_CLIENT_ID")
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise ValueError("Kakao client ID or redirect URI is not set.")

    return KakaoOAuthService(client_id=client_id, redirect_uri=redirect_uri)