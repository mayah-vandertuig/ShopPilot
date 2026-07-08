"""Competitors API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Competitor
from app.schemas import CompetitorRead

router = APIRouter(prefix="/api/analyses", tags=["competitors"])


@router.get("/{analysis_id}/competitors", response_model=list[CompetitorRead])
def get_competitors(analysis_id: int, db: Session = Depends(get_db)):
  competitors = db.query(Competitor).filter(Competitor.analysis_id == analysis_id).all()
  if not competitors:
    raise HTTPException(status_code=404, detail="No competitors found")
  return [
    CompetitorRead(
      id=c.id, analysis_id=c.analysis_id, competitor_name=c.competitor_name,
      platform=c.platform, product_count=c.product_count, average_price=c.average_price,
      total_reviews=c.total_reviews, common_keywords=c.common_keywords,
      positioning_summary=c.positioning_summary,
    )
    for c in competitors
  ]
