"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import database as models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_competitor_columns()
    _ensure_listing_columns()
    _ensure_trend_columns()


def _ensure_listing_columns():
    if not settings.database_url.startswith("sqlite"):
        return

    import sqlalchemy as sa

    with engine.begin() as connection:
        existing = {
            row[1]
            for row in connection.execute(sa.text("PRAGMA table_info(listings)")).fetchall()
        }
        if "listing_source" not in existing:
            connection.execute(
                sa.text("ALTER TABLE listings ADD COLUMN listing_source TEXT DEFAULT 'user'")
            )


def _ensure_trend_columns():
    if not settings.database_url.startswith("sqlite"):
        return

    import sqlalchemy as sa

    with engine.begin() as connection:
        existing = {
            row[1]
            for row in connection.execute(sa.text("PRAGMA table_info(trends)")).fetchall()
        }
        if "details_json" not in existing:
            connection.execute(
                sa.text("ALTER TABLE trends ADD COLUMN details_json TEXT DEFAULT '{}'")
            )


def _ensure_competitor_columns():
    if not settings.database_url.startswith("sqlite"):
        return

    import sqlalchemy as sa

    columns = {
        "average_rating": "REAL DEFAULT 0",
        "matched_queries_json": "TEXT DEFAULT '[]'",
        "example_listing_urls_json": "TEXT DEFAULT '[]'",
        "example_listing_titles_json": "TEXT DEFAULT '[]'",
        "competing_listings_json": "TEXT DEFAULT '[]'",
        "match_score": "REAL DEFAULT 0",
    }
    with engine.begin() as connection:
        existing = {
            row[1]
            for row in connection.execute(sa.text("PRAGMA table_info(competitors)")).fetchall()
        }
        for name, ddl in columns.items():
            if name not in existing:
                connection.execute(sa.text(f"ALTER TABLE competitors ADD COLUMN {name} {ddl}"))
