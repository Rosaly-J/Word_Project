from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.word_search import router as word_search_router
from app.routers.search_bar import router as search_router
from app.routers.bookmark import router as bookmark_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(word_search_router)
app.include_router(search_router)
app.include_router(bookmark_router)