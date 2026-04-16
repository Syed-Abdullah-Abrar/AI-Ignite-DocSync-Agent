"""
Database Connection

SQLAlchemy async connection for patient data persistence.
Uses SQLite for development/prototype, PostgreSQL for production.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Base class for models — available immediately (no engine needed)
Base = declarative_base()

# Lazy-initialized engine and session factory
_engine = None
_session_factory = None


def _get_db_url() -> str:
    """Get the async-compatible database URL.
    
    For the prototype, uses SQLite via aiosqlite.
    For production, switch to PostgreSQL with asyncpg.
    """
    raw_url = os.getenv("DATABASE_URL", "")
    
    if raw_url and raw_url.startswith("postgresql"):
        # Production: convert to async driver
        # postgresql://... → postgresql+asyncpg://...
        return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Development: use SQLite file in project root
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docsync.db")
    return f"sqlite+aiosqlite:///{db_path}"


def get_engine():
    """Get or create the async engine (lazy init)."""
    global _engine
    if _engine is None:
        url = _get_db_url()
        connect_args = {}
        if "sqlite" in url:
            connect_args["check_same_thread"] = False
        _engine = create_async_engine(
            url,
            echo=False,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory():
    """Get or create the session factory (lazy init)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _session_factory


async def get_session() -> AsyncSession:
    """Get async database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
