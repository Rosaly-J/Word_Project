FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 의존성 설치
RUN apt-get update && apt-get install -y libpq-dev gcc curl

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -

# Poetry의 경로를 PATH에 추가
ENV PATH="${PATH}:/root/.local/bin"

# Poetry 설정 (가상 환경 비활성화)
RUN poetry config virtualenvs.create false

# pyproject.toml 및 poetry.lock 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry install --no-dev --no-interaction --no-ansi

# 애플리케이션 소스 복사
COPY . .

# FastAPI 실행 (uvicorn 사용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]