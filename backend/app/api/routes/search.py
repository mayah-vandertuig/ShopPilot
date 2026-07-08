"""Freeform search API."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.freeform_agent import FreeformAgent
from app.database import get_db
from app.exceptions import IngestionError
from app.models.database import Analysis, Competitor, Listing
from app.schemas import FreeformSearchRequest, FreeformSearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/freeform", response_model=FreeformSearchResponse)
def freeform_search(request: FreeformSearchRequest, db: Session = Depends(get_db)):
  analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
  if not analysis:
    raise HTTPException(status_code=404, detail="Analysis not found")

  listings = db.query(Listing).filter(Listing.analysis_id == request.analysis_id).all()
  competitors = db.query(Competitor).filter(Competitor.analysis_id == request.analysis_id).all()

  context = {
    "platform": analysis.platform,
    "input_value": analysis.input_value,
    "pricing_summary": json.loads(analysis.pricing_summary_json or "{}"),
    "keyword_summary": json.loads(analysis.keyword_summary_json or "{}"),
    "listings": [{"title": l.title, "price": l.price, "shop_name": l.shop_name} for l in listings[:20]],
    "competitors": [{"competitor_name": c.competitor_name, "product_count": c.product_count} for c in competitors],
    "listing_count": len(listings),
  }

  agent = FreeformAgent()
  try:
    result = agent.ask(context, request.question)
  except IngestionError as e:
    raise HTTPException(status_code=422, detail=e.message) from e
  return FreeformSearchResponse(**result)
