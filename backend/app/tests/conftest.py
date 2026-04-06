"""测试配置和Fixtures

提供测试所需的共享资源和配置
"""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app


def get_test_engine():
    """创建新的测试引擎（每个测试用独立内存数据库）"""
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """每个测试使用全新的内存数据库"""
    engine = get_test_engine()

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 创建会话
    TestingSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with TestingSessionLocal() as session:
        yield session

    # 清理
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试HTTP客户端"""
    from app.database import get_session

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_device_data():
    """示例设备数据"""
    import uuid
    return {
        "name": f"设备-{uuid.uuid4().hex[:6]}",
        "type": "compressor",
        "location": "测试位置A",
        "status": "online",
    }


@pytest.fixture
def sample_sensor_data():
    """示例传感器数据"""
    return {
        "device_id": 1,
        "temperature": 65.5,
        "vibration": 2.3,
        "current": 12.5,
    }
