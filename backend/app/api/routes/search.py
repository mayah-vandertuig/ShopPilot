"""Freeform search API."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.freeform_agent import FreeformAgent
from app.database import get_db
from app.exceptions import IngestionError
from app.models.database import Analysis, Competitor, Listing, ListingIssue, Trend
from app.schemas import FreeformSearchRequest, FreeformSearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/freeform", response_model=FreeformSearchResponse)
def freeform_search(request: FreeformSearchRequest, db: Session = Depends(get_db)):
  analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
  if not analysis:
    raise HTTPException(status_code=404, detail="Analysis not found")

  question = request.question.strip()
  if not question:
    raise HTTPException(status_code=422, detail="Question cannot be empty")

  listings = db.query(Listing).filter(Listing.analysis_id == request.analysis_id).all()
  if not listings:
    raise HTTPException(
      status_code=422,
      detail="No listings in this analysis. Run a shop or product analysis with scraped data first.",
    )

  competitors = db.query(Competitor).filter(Competitor.analysis_id == request.analysis_id).all()
  issues = db.query(ListingIssue).filter(ListingIssue.analysis_id == request.analysis_id).all()
  trends = db.query(Trend).filter(Trend.analysis_id == request.analysis_id).all()

  context = {
    "platform": analysis.platform,
    "input_type": analysis.input_type,
    "input_value": analysis.input_value,
    "pricing_summary": json.loads(analysis.pricing_summary_json or "{}"),
    "keyword_summary": json.loads(analysis.keyword_summary_json or "{}"),
    "listings": [
      {
        "title": l.title,
        "price": l.price,
        "shop_name": l.shop_name,
        "tags": l.tags,
        "detected_keywords": l.detected_keywords,
      }
      for l in listings[:20]
    ],
    "competitors": [
      {
        "competitor_name": c.competitor_name,
        "product_count": c.product_count,
        "average_price": c.average_price,
        "positioning_summary": c.positioning_summary,
      }
      for c in competitors[:10]
    ],
    "listing_issues": [
      {"category": i.category, "issue": i.issue, "suggestion": i.suggestion}
      for i in issues[:10]
    ],
    "trends": [
      {"trend_name": t.trend_name, "opportunity": t.opportunity}
      for t in trends[:5]
    ],
    "listing_count": len(listings),
    "output_language": "en",
  }

  agent = FreeformAgent()
  try:
    result = agent.ask(context, question)
  except IngestionError as e:
    raise HTTPException(status_code=422, detail=e.message) from e
  return FreeformSearchResponse(**result)
