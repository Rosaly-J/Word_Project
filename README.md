## 프로젝트 폴더 구조

project_root/
├── app/
│   ├── main.py               # FastAPI 애플리케이션 엔트리포인트
│   ├── config.py             # 설정 파일 (예: API 키, 데이터베이스 URL 등)
│   ├── dependencies.py       # 공통 의존성 (예: JWT 검증, DB 세션)
│   ├── routers/              # 주요 기능별 라우터 폴더
│   │   ├── auth.py           # 회원 가입, 로그인, 로그아웃 관련 라우터
│   │   ├── search.py         # 단어 검색 및 자동 완성 라우터
│   │   ├── vocabulary.py     # 단어장 관련 기능 라우터 (단어 등록, 삭제, 조회, 수정)
│   │   ├── learning.py       # 문맥 기반 학습, 미묘한 의미 차이 학습 라우터
│   │   ├── bookmark.py       # 단어 북마크 관련 라우터
│   │   ├── notification.py   # 알림 관련 라우터 (웹소켓 설정 포함)
│   ├── models/               # SQLAlchemy 모델 폴더
│   │   ├── user.py           # 사용자 관련 모델 (회원 가입, 인증 정보)
│   │   ├── word.py           # 단어 관련 모델 (단어 정의, 유의어, 예문 등)
│   │   ├── bookmark.py       # 북마크 모델
│   │   ├── notification.py   # 알림 관련 모델
│   ├── schemas/              # Pydantic 스키마 폴더
│   │   ├── auth.py           # 인증 관련 스키마 (회원가입, 로그인 요청/응답 스키마)
│   │   ├── search.py         # 단어 검색 결과 스키마
│   │   ├── vocabulary.py     # 단어 등록/수정 스키마
│   │   ├── learning.py       # 학습 기능 스키마
│   │   ├── bookmark.py       # 북마크 관련 스키마
│   │   ├── notification.py   # 알림 관련 스키마
│   ├── services/             # 서비스 레이어 폴더 (비즈니스 로직)
│   │   ├── auth_service.py   # Kakao OAuth, JWT 인증 로직
│   │   ├── search_service.py # 단어 검색 및 자동 완성 로직
│   │   ├── learning_service.py # 문맥 기반 학습, 미묘한 의미 차이 학습 로직
│   │   ├── bookmark_service.py # 북마크 로직
│   │   ├── notification_service.py # 알림 서비스 로직 (웹소켓 전송 포함)
│   ├── utils/                # 유틸리티 함수 폴더
│   │   ├── jwt_handler.py    # JWT 토큰 생성 및 검증
│   │   ├── oauth_handler.py  # Kakao OAuth2 통합
│   │   ├── api_caller.py     # OpenAI, dictionaryapi.dev API 호출 함수
│   ├── database/                   # 데이터베이스 초기화 및 연결 폴더
│   │   ├── db.py       # SQLAlchemy 세션 관리 및 DB 연결 설정
│   │   ├── init_db.py        # 초기 데이터베이스 스키마 생성
│   └── websocket/            # 웹소켓 관련 설정
│       └── connection.py     # WebSocket 연결 설정 및 핸들러
│       └── events.py         # WebSocket 이벤트 관리
└── requirements.txt          # 패키지 종속성 목록