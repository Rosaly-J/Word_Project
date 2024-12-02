from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, DateTime, Enum, Boolean, BigInteger,Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# 비동기 엔진 설정
DATABASE_URL = "postgresql+asyncpg://hwi:1234@localhost/voca"
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kakao_id = Column(Integer, unique=True, nullable=False)  # 카카오 고유 ID
    email = Column(String, unique=True, nullable=True)      # 이메일 (카카오 계정)
    nickname = Column(String, nullable=False)               # 닉네임
    password = Column(String, nullable=True)               # 쇼설 로그인이라 이쪽에서 관리 안해서 nullable=True
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")  # 생성 날짜

    # SearchHistory와의 관계 설정
    search_history = relationship("SearchHistory", back_populates="user")
    # BookmarkWord와의 관계 설정
    bookmark_words = relationship("BookmarkWord", back_populates="user", cascade="all, delete-orphan")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="search_history", cascade="all, delete")

    def to_dict(self):
        """
        객체를 JSON 직렬화 가능한 딕셔너리로 변환
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "word": self.word,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class StudyCategory(PyEnum):
    VOCABULARY = "Vocabulary"
    GRAMMAR = "Grammar"
    READING = "Reading"
    WRITING = "Writing"


class BookmarkWord(Base):
    __tablename__ = "bookmark_words"
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "search_term": self.search_term,
            "timestamp": self.timestamp,
        }
    word_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID 타입의 PK
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # 사용자 ID
    word = Column(String(25), nullable=False)  # 단어
    definition = Column(String(255), nullable=True)  # 단어 의미
    example = Column(Text, nullable=True)  # 예시 문장
    bookmark = Column(Boolean, nullable=False, default=True)  # 북마크 여부
    study_category = Column(Enum(StudyCategory), nullable=False, default=StudyCategory.VOCABULARY)  # 학습 종류 (ENUM)

    # 관계 설정
    user = relationship("User", back_populates="bookmark_words")
