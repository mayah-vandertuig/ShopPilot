"""Analysis API routes."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Analysis, Competitor, Listing, ListingIssue, Recommendation, Trend
from app.schemas import (
  AnalysisCreate,
  AnalysisCreateResponse,
  AnalysisDetail,
  AnalysisRead,
  CompetitorRead,
  KeywordSummary,
  ListingRead,
  PricingSummary,
)
from app.services.analysis_runner import AnalysisRunner
from app.agents.listing_advisor import ListingAdvisorAgent
from app.agents.product_expansion_agent import ProductExpansionAgent
from app.services.ai import AIService

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


def _analysis_to_detail(analysis: Analysis, db: Session, warning: str = None) -> AnalysisDetail:
  listings = db.query(Listing).filter(Listing.analysis_id == analysis.id).all()
  competitors = db.query(Competitor).filter(Competitor.analysis_id == analysis.id).all()
  issues = db.query(ListingIssue).filter(ListingIssue.analysis_id == analysis.id).all()
  recommendations = db.query(Recommendation).filter(Recommendation.analysis_id == analysis.id).all()
  trends = db.query(Trend).filter(Trend.analysis_id == analysis.id).all()

  pricing = PricingSummary(**json.loads(analysis.pricing_summary_json or "{}"))
  keywords = KeywordSummary(**json.loads(analysis.keyword_summary_json or "{}"))

  listing_reads = []
  for l in listings:
    listing_reads.append(ListingRead(
      id=l.id, analysis_id=l.analysis_id, platform=l.platform, title=l.title,
      url=l.url, shop_name=l.shop_name, price=l.price, currency=l.currency,
      rating=l.rating, review_count=l.review_count, image_url=l.image_url,
      description=l.description, tags=l.tags, detected_keywords=l.detected_keywords,
    ))

  return AnalysisDetail(
    id=analysis.id, platform=analysis.platform, input_type=analysis.input_type,
    input_value=analysis.input_value, country=analysis.country, currency=analysis.currency,
    status=analysis.status, data_source=analysis.data_source,
    created_at=analysis.created_at, updated_at=analysis.updated_at,
    pricing_summary=pricing, keyword_summary=keywords,
    listings=listing_reads,
    competitors=[CompetitorRead(
      id=c.id, analysis_id=c.analysis_id, competitor_name=c.competitor_name,
      platform=c.platform, product_count=c.product_count, average_price=c.average_price,
      total_reviews=c.total_reviews, common_keywords=c.common_keywords,
      positioning_summary=c.positioning_summary,
    ) for c in competitors],
    listing_issues=issues,
    recommendations=recommendations,
    trends=trends,
    warning=warning,
  )


@router.post("", response_model=AnalysisCreateResponse)
def create_analysis(request: AnalysisCreate, db: Session = Depends(get_db)):
  runner = AnalysisRunner()
  analysis = runner.run(db, request)
  warning = getattr(analysis, "_warning", None)
  if analysis.data_source == "mock" and not warning:
    warning = "Using mock sample data. Set BRIGHT_DATA_API_KEY for live marketplace data."
  return _analysis_to_detail(analysis, db, warning)


@router.get("", response_model=List[AnalysisRead])
def list_analyses(db: Session = Depends(get_db)):
  analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(50).all()
  result = []
  for a in analyses:
    pricing = PricingSummary(**json.loads(a.pricing_summary_json or "{}"))
    keywords = KeywordSummary(**json.loads(a.keyword_summary_json or "{}"))
    result.append(AnalysisRead(
      id=a.id, platform=a.platform, input_type=a.input_type, input_value=a.input_value,
      country=a.country, currency=a.currency, status=a.status, data_source=a.data_source,
      created_at=a.created_at, updated_at=a.updated_at,
      pricing_summary=pricing, keyword_summary=keywords,
    ))
  return result


@router.get("/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
  analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
  if not analysis:
    raise HTTPException(status_code=404, detail="Analysis not found")
  return _analysis_to_detail(analysis, db)


@router.post("/{analysis_id}/recommendations")
def generate_recommendations(analysis_id: int, db: Session = Depends(get_db)):
  analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
  if not analysis:
    raise HTTPException(status_code=404, detail="Analysis not found")

  listings = db.query(Listing).filter(Listing.analysis_id == analysis_id).all()
  competitors = db.query(Competitor).filter(Competitor.analysis_id == analysis_id).all()
  pricing = json.loads(analysis.pricing_summary_json or "{}")
  keywords = json.loads(analysis.keyword_summary_json or "{}")

  advisor = ListingAdvisorAgent()
  expansion = ProductExpansionAgent()
  ai = AIService()

  context = {
    "listings": [{"title": l.title, "price": l.price, "shop_name": l.shop_name} for l in listings[:10]],
    "competitors": [{"competitor_name": c.competitor_name, "average_price": c.average_price} for c in competitors],
    "pricing_summary": pricing,
    "keyword_summary": keywords,
  }

  recs = ai.generate_listing_recommendations(context)
  expansion_result = expansion.expand(
    [{"title": l.title, "price": l.price} for l in listings],
    [],
    [{"competitor_name": c.competitor_name} for c in competitors],
  )

  new_recs = []
  for r in recs:
    rec = Recommendation(
      analysis_id=analysis_id,
      category=r.get("category", "general"),
      recommendation=r.get("recommendation", ""),
      reasoning=r.get("reasoning", ""),
      confidence=r.get("confidence", 0.5),
    )
    db.add(rec)
    new_recs.append(rec)

  for idea in expansion_result.get("product_ideas", []):
    rec = Recommendation(
      analysis_id=analysis_id,
      category="product_expansion",
      recommendation=idea.get("idea", ""),
      reasoning=idea.get("rationale", ""),
      confidence=idea.get("confidence", 0.5),
    )
    db.add(rec)
    new_recs.append(rec)

  db.commit()
  return {
    "recommendations": [
      {"category": r.category, "recommendation": r.recommendation, "reasoning": r.reasoning, "confidence": r.confidence}
      for r in new_recs
    ],
    "expansion": expansion_result,
    "data_source": "live" if ai.settings.has_openai else "mock",
  }
