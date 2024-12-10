from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.word_search import router as word_search_router
from app.routers.search_bar import router as search_router
from app.routers.bookmark import router as bookmark_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # 허용할 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],                     # 허용할 HTTP 메서드
    allow_headers=["*"],                     # 허용할 HTTP 헤더
)

app.include_router(auth_router)
app.include_router(word_search_router)
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(bookmark_router)