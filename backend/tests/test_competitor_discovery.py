"""Tests for competitor discovery and scoring."""

from unittest.mock import MagicMock

from app.analysis.competitor_discovery import generate_competitor_queries, is_own_shop
from app.analysis.competitors import analyze_competitors, compute_match_score
from app.schemas import ProductListingSchema
from app.services.ingestion import IngestionService
from app.services.mock_marketplace import USER_SHOP, mock_shop_analysis_bundle


def _listing(
    title: str,
    shop_name: str,
    price: float = 20.0,
    query: str = "minimalist wall art",
    position: int = 0,
    reviews: int = 10,
    rating: float = 4.5,
    listing_source: str = "competitor_search",
) -> ProductListingSchema:
    return ProductListingSchema(
        platform="etsy",
        title=title,
        shop_name=shop_name,
        price=price,
        review_count=reviews,
        rating=rating,
        tags=["minimalist", "wall art"],
        description=f"{title} for modern home decor",
        listing_source=listing_source,
        raw_data={
            "matched_query": query,
            "search_position": position,
            "listing_source": listing_source,
        },
    )


def test_generate_competitor_queries_from_user_listings():
    user_listings = [
        ProductListingSchema(
            platform="etsy",
            title="Minimalist Line Art Canvas Print",
            shop_name=USER_SHOP,
            price=28.0,
            tags=["minimalist", "canvas", "line art"],
            description="Neutral minimalist wall art for living room",
            listing_source="user_shop",
        ),
        ProductListingSchema(
            platform="etsy",
            title="Abstract Beige Wall Art Set",
            shop_name=USER_SHOP,
            price=32.0,
            tags=["abstract", "beige", "wall art"],
            description="Beige abstract poster for bedroom decor",
            listing_source="user_shop",
        ),
    ]

    queries = generate_competitor_queries(user_listings, USER_SHOP)

    assert queries
    assert any("minimalist" in query.lower() for query in queries)
    assert any("abstract" in query.lower() or "beige" in query.lower() for query in queries)
    assert not any(USER_SHOP.lower() in query.lower().replace(" ", "") for query in queries)


def test_excludes_users_own_shop():
    user_listings = [
        ProductListingSchema(platform="etsy", title="My Listing", shop_name=USER_SHOP, price=25.0, listing_source="user_shop"),
    ]
    competitor_listings = [
        _listing("Competitor A", "ModernPrintLab", query="minimalist wall art"),
        _listing("My Other Listing", USER_SHOP, query="minimalist wall art"),
        _listing("Competitor B", "NordicPosterCo", query="minimalist wall art"),
    ]

    result = analyze_competitors(
        competitor_listings,
        analysis_id=1,
        platform="etsy",
        user_listings=user_listings,
        exclude_shop_keys={"sanfranciscostudio"},
    )

    names = {item["competitor_name"] for item in result}
    assert USER_SHOP not in names
    assert "ModernPrintLab" in names


def test_groups_listings_by_competitor_shop():
    listings = [
        _listing("A1", "ShopOne", query="minimalist wall art", position=0),
        _listing("A2", "ShopOne", query="abstract beige print", position=2),
        _listing("B1", "ShopTwo", query="minimalist wall art", position=1),
    ]

    result = analyze_competitors(listings, 1, "etsy")
    shop_one = next(item for item in result if item["competitor_name"] == "ShopOne")

    assert shop_one["product_count"] == 2
    assert "minimalist wall art" in shop_one["matched_queries"]


def test_competitor_score_and_ranking_order():
    user_listings = [
        ProductListingSchema(
            platform="etsy",
            title="Minimalist Line Art Canvas",
            shop_name="ArtStudioCo",
            price=30.0,
            tags=["minimalist", "canvas"],
        )
    ]
    listings = [
        _listing("Minimalist Canvas One", "AlphaStudio", price=29.0, query="minimalist canvas", position=0, reviews=120, rating=4.8),
        _listing("Minimalist Canvas Two", "AlphaStudio", price=31.0, query="minimalist canvas", position=1, reviews=80, rating=4.7),
        _listing("Random Decor", "LowMatchShop", price=80.0, query="vintage decor", position=15, reviews=5, rating=3.5),
    ]

    result = analyze_competitors(
        listings,
        1,
        "etsy",
        user_listings=user_listings,
        exclude_shop_keys={"artstudioco"},
    )

    assert result[0]["competitor_name"] == "AlphaStudio"
    assert result[0]["match_score"] > result[1]["match_score"]
    assert result[0]["match_score"] >= 40


def test_compute_match_score_rewards_overlap_and_reviews():
    score = compute_match_score(
        user_keywords={"minimalist", "canvas", "wall"},
        user_avg_price=30.0,
        product_count=3,
        query_hits=2,
        total_reviews=200,
        average_rating=4.8,
        keyword_overlap_ratio=0.7,
        price_similarity=0.9,
        position_score=0.8,
    )
    assert score >= 60


def test_mock_shop_bundle_has_realistic_competitor_grouping():
    user_listings, competitor_listings = mock_shop_analysis_bundle(shop_name=USER_SHOP)

    assert len(user_listings) >= 8
    assert len(competitor_listings) >= 30
    assert len({listing.shop_name for listing in competitor_listings}) >= 6
    assert all(listing.shop_name != USER_SHOP for listing in competitor_listings)
    assert all(listing.listing_source == "competitor_search" for listing in competitor_listings)
    assert all(listing.listing_source == "user_shop" for listing in user_listings)


def test_is_own_shop_normalizes_names():
    assert is_own_shop("San-Francisco-Studio", {"sanfranciscostudio"})
    assert not is_own_shop("ModernPrintLab", {"sanfranciscostudio"})


def test_user_shop_is_excluded_from_competitors():
    user_listings, competitor_listings = mock_shop_analysis_bundle(shop_name=USER_SHOP)
    mixed = competitor_listings + [
        _listing("Own listing in search", USER_SHOP, query="minimalist wall art", listing_source="competitor_search"),
        _listing("Own listing user source", USER_SHOP, query="minimalist wall art", listing_source="user_shop"),
    ]

    result = analyze_competitors(
        mixed,
        analysis_id=1,
        platform="etsy",
        user_listings=user_listings,
        exclude_shop_keys={"sanfranciscostudio"},
    )

    assert USER_SHOP not in {item["competitor_name"] for item in result}
    assert len(result) >= 6


def test_competitors_are_grouped_from_competitor_search_listings_only():
    listings = [
        _listing("Comp A", "ModernPrintLab"),
        _listing("Comp B", "ModernPrintLab"),
        ProductListingSchema(
            platform="etsy",
            title="User shop listing",
            shop_name="ShouldNotGroup",
            price=20.0,
            listing_source="user_shop",
            raw_data={"listing_source": "user_shop"},
        ),
    ]

    result = analyze_competitors(listings, 1, "etsy")

    names = {item["competitor_name"] for item in result}
    assert "ModernPrintLab" in names
    assert "ShouldNotGroup" not in names
    assert result[0]["product_count"] == 2


def test_generated_queries_are_used_to_fetch_competitor_listings(monkeypatch):
    user_listings = mock_shop_analysis_bundle(shop_name=USER_SHOP)[0]
    queries_seen = []

    def fake_search(platform, query, country="", currency="", language="", locale=""):
        queries_seen.append(query)
        return [], "live", "", ""

    service = IngestionService()
    service.bright_data = MagicMock()
    service.bright_data.is_available = True
    service.bright_data.search_marketplace = fake_search

    from app.adapters.etsy import EtsyAdapter

    adapter = EtsyAdapter()
    listings, warning, source, queries = service._discover_competitor_listings(
        "etsy",
        adapter,
        USER_SHOP,
        user_listings,
        "US",
        "USD",
        "en-US",
        "en_US",
    )

    assert queries_seen
    assert set(queries_seen).issubset(set(queries))
    assert len({listing.shop_name for listing in listings}) >= 6


def test_multiple_competitor_shops_are_returned():
    user_listings, competitor_listings = mock_shop_analysis_bundle(shop_name=USER_SHOP)

    result = analyze_competitors(
        competitor_listings,
        analysis_id=1,
        platform="etsy",
        user_listings=user_listings,
        exclude_shop_keys={"sanfranciscostudio"},
    )

    names = {item["competitor_name"] for item in result}
    assert len(names) >= 6
    assert "ModernPrintLab" in names
    assert "NeutralGalleryCo" in names
    assert USER_SHOP not in names


def test_empty_competitor_state_does_not_show_user_shop():
    user_listings = mock_shop_analysis_bundle(shop_name=USER_SHOP)[0]
    user_only_as_competitors = [
        ProductListingSchema(
            platform="etsy",
            title=listing.title,
            shop_name=USER_SHOP,
            price=listing.price,
            listing_source="user_shop",
            raw_data={"listing_source": "user_shop"},
        )
        for listing in user_listings
    ]

    result = analyze_competitors(
        user_only_as_competitors,
        analysis_id=1,
        platform="etsy",
        user_listings=user_listings,
        exclude_shop_keys={"sanfranciscostudio"},
    )

    assert result == []
