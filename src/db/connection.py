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
    # Import models so they register with Base.metadata
    import src.db.models  # noqa: F401
    
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


async def seed_patients_if_empty():
    """
    Seed the patients table from data/patients.json if empty.
    
    Only seeds if no patients exist in the database.
    """
    import json
    import os
    import logging

    logger = logging.getLogger(__name__)

    # Import here to avoid circular issues
    from src.db.models import Patient

    engine = get_engine()

    # Check if patients already exist (table might not exist on first run)
    from sqlalchemy import text
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM patients"))
            count = result.scalar()
            if count and count > 0:
                logger.info(f"Database already has {count} patients, skipping seed")
                return
    except Exception:
        # Table doesn't exist yet or other issue — proceed with seeding
        pass

    # Load patient data
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    patients_path = os.path.join(project_root, "data", "patients.json")

    if not os.path.exists(patients_path):
        logger.warning(f"Seed file not found: {patients_path}")
        return

    with open(patients_path, "r") as f:
        data = json.load(f)

    patients_list = data.get("patients", [])
    if not patients_list:
        logger.warning("No patients found in seed file")
        return

    # Insert using SQLAlchemy Core (not ORM session — we're on a raw connection)
    from sqlalchemy import insert
    async with engine.begin() as conn:
        for patient_data in patients_list:
            # Convert lists to JSON-compatible format for SQLite
            await conn.execute(
                insert(Patient.__table__).values(
                    id=patient_data["id"],
                    phone_number=patient_data["phone_number"],
                    name=patient_data["name"],
                    medical_history=patient_data.get("medical_history", []),
                    allergies=patient_data.get("allergies", []),
                    current_medications=patient_data.get("current_medications", []),
                )
            )

    logger.info(f"Seeded {len(patients_list)} patients from {patients_path}")
