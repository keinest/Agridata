"""Database configuration and initialization."""
import logging
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
database_url = settings.SQLALCHEMY_DATABASE_URL
engine_kwargs = {
    "echo": settings.DEBUG,
}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "poolclass": pool.QueuePool,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
        }
    )

engine = create_engine(database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def init_db():
    """Initialize database - create tables if not exist"""
    try:
        # Import models to register them with Base
        from app.infrastructure.models import (
            User, Tenant, Exploitation, Parcelle, Rendement,
            MeteoData, SolQualite, Intrant, Alerte, Rapport,
            AnalysisPrediction, AuditLog
        )
        
        # Create all tables
        Base.metadata.create_all(bind = engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db():
    """Get database session - dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
