import asyncio
from logging.config import fileConfig
from config.settings import Settings
from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine
from database.db import Base # db.py에서 Base 가져오기
import warnings

from alembic import context
from app.database.db import SQLALCHEMY_DATABASE_URL


config = context.config
fileConfig(config.config_file_name)

warnings.filterwarnings("ignore", category=RuntimeWarning)
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config # Alembic Config 객체
fileConfig(config.config_file_name)

# 데이터베이스 URL 설정
# .env 파일에서 가져온 PostgreSQL 연결 URL을 사용합니다.
settings = Settings()
SQLALCHEMY_DATABASE_URL = settings.database_url  # settings에서 불러오는 PostgreSQL 연결 URL
target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# metadata 설정
# Base.metadata를 통해 모든 모델의 테이블 정보를 가져옵니다.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# engine 생성
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)


# engine 생성
async def run_migrations_online():

    connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_connection: context.configure(
                connection=sync_connection,
                target_metadata=target_metadata,
                render_as_batch=True, # 필요 시 활성화
            )
        )

        async with connection.begin():
            context.run_migrations()


# Alembic 실행 모드에 맞는 함수 호출
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

    print("ok")