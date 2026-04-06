"""测试配置和Fixtures

提供测试所需的共享资源和配置
"""

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app

# 使用文件数据库进行测试（每个测试后清理）
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# 测试会话工厂
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """测试会话开始时创建表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # 测试会话结束时清理
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await test_engine.dispose()
    # 删除测试数据库文件
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话，每个测试后清理数据"""
    async with TestingSessionLocal() as session:
        yield session
        # 清理所有数据
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试HTTP客户端"""
    # 覆盖依赖
    from app.database import get_session

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 清除覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_device_data():
    """示例设备数据"""
    import uuid
    return {
        "name": f"测试设备-{uuid.uuid4().hex[:8]}",
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
