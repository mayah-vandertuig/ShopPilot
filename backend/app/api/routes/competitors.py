"""Competitors API routes."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analysis.competitors import DISCOVERED_LABEL, build_competitor_detail, _shop_key
from app.database import get_db
from app.models.database import Analysis, Competitor, Listing
from app.schemas import CompetitorDetailRead, CompetitorRead, ProductListingSchema

router = APIRouter(prefix="/api/analyses", tags=["competitors"])


def _competitor_to_read(competitor: Competitor) -> CompetitorRead:
    return CompetitorRead(
        id=competitor.id,
        analysis_id=competitor.analysis_id,
        competitor_name=competitor.competitor_name,
        platform=competitor.platform,
        product_count=competitor.product_count,
        average_price=competitor.average_price,
        total_reviews=competitor.total_reviews,
        average_rating=competitor.average_rating,
        common_keywords=competitor.common_keywords,
        matched_queries=competitor.matched_queries,
        example_listing_urls=competitor.example_listing_urls,
        example_listing_titles=competitor.example_listing_titles,
        match_score=competitor.match_score,
        positioning_summary=competitor.positioning_summary,
    )


def _user_listings_for_analysis(db: Session, analysis_id: int) -> list[ProductListingSchema]:
    listings = (
        db.query(Listing)
        .filter(Listing.analysis_id == analysis_id)
        .filter(Listing.listing_source.in_(["user_shop", "user"]))
        .all()
    )
    return [
        ProductListingSchema(
            platform=listing.platform,
            title=listing.title,
            url=listing.url,
            shop_name=listing.shop_name,
            price=listing.price,
            currency=listing.currency,
            rating=listing.rating,
            review_count=listing.review_count,
            image_url=listing.image_url,
            description=listing.description,
            tags=listing.tags,
            detected_keywords=listing.detected_keywords,
            raw_data=json.loads(listing.raw_data_json or "{}"),
        )
        for listing in listings
    ]


@router.get("/{analysis_id}/competitors", response_model=list[CompetitorRead])
def get_competitors(analysis_id: int, db: Session = Depends(get_db)):
    competitors = (
        db.query(Competitor)
        .filter(Competitor.analysis_id == analysis_id)
        .order_by(Competitor.match_score.desc(), Competitor.product_count.desc())
        .all()
    )
    if not competitors:
        raise HTTPException(status_code=404, detail="No discovered competitors found")
    return [_competitor_to_read(competitor) for competitor in competitors]


def _competitor_listings_for_shop(db: Session, analysis_id: int, shop_name: str) -> list[ProductListingSchema]:
    target_key = _shop_key(shop_name)
    listings = (
        db.query(Listing)
        .filter(Listing.analysis_id == analysis_id)
        .filter(Listing.listing_source.in_(["competitor_search", "competitor"]))
        .all()
    )
    results: list[ProductListingSchema] = []
    for listing in listings:
        if _shop_key(listing.shop_name) != target_key:
            continue
        results.append(
            ProductListingSchema(
                platform=listing.platform,
                title=listing.title,
                url=listing.url,
                shop_name=listing.shop_name,
                price=listing.price,
                currency=listing.currency,
                rating=listing.rating,
                review_count=listing.review_count,
                image_url=listing.image_url,
                description=listing.description,
                tags=listing.tags,
                detected_keywords=listing.detected_keywords,
                listing_source=listing.listing_source,
                raw_data=json.loads(listing.raw_data_json or "{}"),
            )
        )
    return results


@router.get("/{analysis_id}/competitors/{competitor_id}", response_model=CompetitorDetailRead)
def get_competitor_detail(analysis_id: int, competitor_id: int, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    competitor = (
        db.query(Competitor)
        .filter(Competitor.id == competitor_id, Competitor.analysis_id == analysis_id)
        .first()
    )
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    user_listings = _user_listings_for_analysis(db, analysis_id)
    competitor_listings = _competitor_listings_for_shop(db, analysis_id, competitor.competitor_name)
    if not competitor_listings and competitor.competing_listings:
        competitor_listings = [
            ProductListingSchema(
                platform=competitor.platform,
                title=item.get("title", ""),
                url=item.get("url", ""),
                shop_name=competitor.competitor_name,
                price=float(item.get("price", 0) or 0),
                rating=float(item.get("rating", 0) or 0),
                review_count=int(item.get("review_count", 0) or 0),
                image_url=item.get("image_url", ""),
                listing_source="competitor_search",
            )
            for item in competitor.competing_listings
        ]

    detail = build_competitor_detail(
        _competitor_to_read(competitor).model_dump(),
        user_listings,
        competitor_listings,
    )
    detail["competing_listings"] = [
        {
            "title": listing.title,
            "url": listing.url,
            "price": listing.price,
            "rating": listing.rating,
            "review_count": listing.review_count,
            "image_url": listing.image_url,
        }
        for listing in competitor_listings[:12]
    ] or competitor.competing_listings or []
    detail["discovered_label"] = DISCOVERED_LABEL
    return CompetitorDetailRead(**detail)
