"""ShopPilot FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyses, codex, competitors, health, listings, search
from app.config import get_settings
from app.database import init_db

settings = get_settings()

app = FastAPI(
  title="ShopPilot API",
  description="AI-powered marketplace intelligence platform",
  version="1.0.0",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyses.router)
app.include_router(listings.router)
app.include_router(competitors.router)
app.include_router(search.router)
app.include_router(codex.router)


@app.on_event("startup")
def startup():
  init_db()
