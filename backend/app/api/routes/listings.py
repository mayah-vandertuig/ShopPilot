"""Listings API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Listing
from app.schemas import ListingRead

router = APIRouter(prefix="/api/analyses", tags=["listings"])


@router.get("/{analysis_id}/listings", response_model=list[ListingRead])
def get_listings(analysis_id: int, db: Session = Depends(get_db)):
  listings = db.query(Listing).filter(Listing.analysis_id == analysis_id).all()
  if not listings:
    raise HTTPException(status_code=404, detail="No listings found")
  return [
    ListingRead(
      id=l.id, analysis_id=l.analysis_id, platform=l.platform, title=l.title,
      url=l.url, shop_name=l.shop_name, price=l.price, currency=l.currency,
      rating=l.rating, review_count=l.review_count, image_url=l.image_url,
      description=l.description, tags=l.tags, detected_keywords=l.detected_keywords,
    )
    for l in listings
  ]
