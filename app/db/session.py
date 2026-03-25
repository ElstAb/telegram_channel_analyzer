from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db import models  # noqa: F401  (needed to register models)

engine = create_engine(settings.database_url)

# Ensure DB schema (tables) is created if missing
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)