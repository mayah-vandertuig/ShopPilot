"""Tests for tag intelligence analysis."""

from app.analysis.tag_intelligence import (
    analyze_tag_intelligence,
    build_keyword_insights,
    calculate_opportunity_score,
    calculate_tag_gap,
    classify_keyword_type,
    extract_tags_from_competitor_listings,
    extract_tags_from_user_listings,
    generate_long_tail_opportunities,
    estimate_keyword_competition,
    estimate_keyword_demand,
)
from app.schemas import ProductListingSchema


def _user_listing(title: str, tags: list, **kwargs) -> ProductListingSchema:
    return ProductListingSchema(
        platform="etsy",
        title=title,
        tags=tags,
        **kwargs,
    )


def _competitor_listing(title: str, tags: list, shop_name: str = "CompShop", **kwargs) -> ProductListingSchema:
    return ProductListingSchema(
        platform="etsy",
        title=title,
        shop_name=shop_name,
        tags=tags,
        raw_data=kwargs.pop("raw_data", {"matched_query": "minimalist wall art", "search_position": 5}),
        **kwargs,
    )


def test_extract_tags_from_user_listings():
    listings = [
        _user_listing("Minimalist Wall Art Print", ["minimalist wall art", "botanical print"]),
        _user_listing("Botanical Poster", ["botanical print", "neutral wall art"]),
    ]
    counts = extract_tags_from_user_listings(listings)
    assert counts["minimalist wall art"] >= 1
    assert counts["botanical print"] >= 2


def test_extract_tags_from_competitor_listings():
    listings = [
        _competitor_listing("Neutral Botanical Print", ["neutral botanical print", "botanical wall art"]),
        _competitor_listing("Kitchen Citrus Wall Art", ["kitchen citrus wall art", "kitchen wall art"]),
    ]
    counts = extract_tags_from_competitor_listings(listings, search_queries=["neutral botanical print"])
    assert counts["neutral botanical print"] >= 1
    assert counts["botanical wall art"] >= 1


def test_classify_keyword_type():
    assert classify_keyword_type("minimalist poster") == "style"
    assert classify_keyword_type("kitchen wall art") == "room"
    assert classify_keyword_type("botanical print") == "theme"
    assert classify_keyword_type("digital download") == "format"
    assert classify_keyword_type("gallery wall set") == "product"


def test_calculate_tag_gap():
    user_counts = extract_tags_from_user_listings([
        _user_listing("Minimalist Print", ["minimalist wall art", "wall art"]),
        _user_listing("Abstract Art", ["abstract poster", "wall art"]),
    ])
    competitor_counts = extract_tags_from_competitor_listings([
        _competitor_listing("Botanical Print", ["botanical wall art", "neutral botanical print"]),
        _competitor_listing("Botanical Art", ["botanical wall art", "nursery wall art"]),
    ])
    gap = calculate_tag_gap(user_counts, competitor_counts)
    assert "botanical wall art" in gap["missing_tags"]
    assert "wall art" in gap["weak_generic_tags"] or "wall art" in gap["user_frequent_tags"]


def test_estimate_keyword_demand_and_competition():
    assert estimate_keyword_demand("botanical wall art", 10) == "High"
    assert estimate_keyword_demand("niche tag", 1) == "Low"
    assert estimate_keyword_competition("wall art", 20, 5) == "High"
    assert estimate_keyword_competition("neutral botanical print", 3, 10) == "Low"


def test_calculate_opportunity_score():
    user_counts = extract_tags_from_user_listings([
        _user_listing("Test", ["minimalist wall art"]),
    ])
    score_missing = calculate_opportunity_score(
        "neutral botanical print", 8, 0, "High", "Medium", "rising", user_counts
    )
    score_overused = calculate_opportunity_score(
        "wall art", 5, 5, "Medium", "High", "stable", user_counts
    )
    assert 0 <= score_missing <= 100
    assert score_missing > score_overused


def test_generate_long_tail_opportunities():
    user = [_user_listing("Minimalist Print", ["minimalist wall art"])]
    competitors = [
        _competitor_listing("Neutral Botanical", ["neutral botanical print", "botanical wall art"]),
        _competitor_listing("Kitchen Citrus", ["kitchen citrus wall art"]),
    ]
    insights = build_keyword_insights(user, competitors, ["neutral botanical print"])
    long_tail = generate_long_tail_opportunities(insights, competitors)
    assert len(long_tail) >= 1
    assert all(len(item["tag"].split()) >= 2 for item in long_tail)


def test_user_vs_competitor_tag_comparison():
    user = [
        _user_listing("Minimalist Line Art", ["minimalist wall art", "line art print"]),
        _user_listing("Abstract Beige", ["abstract poster", "beige wall decor"]),
    ]
    competitors = [
        _competitor_listing("Botanical Print", ["botanical wall art", "neutral botanical print"], "ShopA"),
        _competitor_listing("Botanical Art", ["botanical wall art", "nursery wall art"], "ShopB"),
        _competitor_listing("Gallery Set", ["gallery wall set", "printable gallery wall set"], "ShopC"),
    ]
    result = analyze_tag_intelligence(user, competitors)
    assert result["summary_stats"]["total_tags_analyzed"] > 0
    assert len(result["tag_insights"]) > 0
    assert len(result["missing_tag_opportunities"]) >= 1
    assert "user_frequent_tags" in result["tag_gap_analysis"]
