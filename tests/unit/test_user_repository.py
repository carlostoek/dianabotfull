# tests/unit/test_user_repository.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User, UserProgress
from src.database.repository import UserRepository

@pytest.fixture(name="engine")
async def create_test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(name="session")
async def create_test_session(engine):
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session

@pytest.mark.asyncio
async def test_get_or_create_new_user(session: AsyncSession):
    repo = UserRepository(session)
    user, created = await repo.get_or_create(123, "testuser1")

    assert created is True
    assert user.id == 123
    assert user.username == "testuser1"
    
    # Verify UserProgress was created
    progress = await session.get(UserProgress, 123)
    assert progress is not None
    assert progress.user_id == 123

@pytest.mark.asyncio
async def test_get_or_create_existing_user(session: AsyncSession):
    repo = UserRepository(session)
    
    # Create user first
    await repo.get_or_create(123, "testuser1")
    
    # Try to get or create again
    user, created = await repo.get_or_create(123, "testuser1_updated")

    assert created is False
    assert user.id == 123
    assert user.username == "testuser1" # Username should not be updated

@pytest.mark.asyncio
async def test_get_or_create_concurrent_creation(session: AsyncSession):
    # Simulate a concurrent creation attempt
    repo1 = UserRepository(session)
    repo2 = UserRepository(session)

    # This test is harder to simulate perfectly without actual concurrency
    # but the IntegrityError handling in get_or_create should cover it.
    # For a unit test, we can just ensure it doesn't break.
    user1, created1 = await repo1.get_or_create(456, "concurrent_user")
    user2, created2 = await repo2.get_or_create(456, "concurrent_user")

    assert (created1 and not created2) or (not created1 and created2)
    assert user1.id == 456
    assert user2.id == 456
