"""Realistic mock marketplace data for shop and competitor discovery."""

from typing import List, Tuple

from app.schemas import ProductListingSchema

USER_SHOP = "SanFranciscoStudio"

COMPETITOR_SHOPS = [
    ("ModernPrintLab", 5, 24.0),
    ("NordicPosterCo", 5, 28.0),
    ("BotanicalRoomPrints", 5, 26.0),
    ("AbstractWallStudio", 5, 30.0),
    ("PrintableArtHouse", 5, 22.0),
    ("NeutralGalleryCo", 5, 32.0),
]

REALISTIC_ETSY_TAGS = [
    "minimalist wall art",
    "botanical print",
    "neutral wall art",
    "printable wall art",
    "gallery wall set",
    "kitchen wall art",
    "abstract poster",
    "bauhaus print",
    "digital download",
    "nursery wall art",
    "vintage landscape",
    "coastal wall art",
    "modern art print",
    "beige wall decor",
    "instant download",
    "neutral botanical print",
    "kitchen citrus wall art",
    "printable gallery wall set",
    "beige abstract poster",
    "modern nursery wall art",
    "minimalist poster",
    "botanical wall art",
    "abstract wall art",
    "scandinavian print",
    "line art print",
    "geometric wall art",
    "living room decor",
    "bedroom wall art",
    "office wall art",
    "printable art",
]


def mock_user_shop_listings(
    shop_name: str = USER_SHOP,
    platform: str = "etsy",
    currency: str = "USD",
) -> List[ProductListingSchema]:
    titles = [
        "Minimalist Line Art Canvas Print",
        "Abstract Beige Wall Art Set",
        "Scandinavian Botanical Poster",
        "Neutral Geometric Line Drawing",
        "Modern Black White Wall Decor",
        "Handmade Minimalist Home Print",
        "Beige Abstract Living Room Art",
        "Simple Line Art Bedroom Poster",
    ]
    tags = [
        ["minimalist wall art", "line art print", "canvas print"],
        ["abstract poster", "beige wall decor", "gallery wall set"],
        ["botanical print", "scandinavian print", "neutral wall art"],
        ["geometric wall art", "neutral wall art", "modern art print"],
        ["minimalist poster", "black white decor", "living room decor"],
        ["minimalist wall art", "handmade print", "modern art print"],
        ["beige abstract poster", "abstract wall art", "living room decor"],
        ["line art print", "bedroom wall art", "minimalist poster"],
    ]
    listings: List[ProductListingSchema] = []
    for index, title in enumerate(titles, start=1):
        listings.append(
            ProductListingSchema(
                platform=platform,
                title=title,
                url=f"https://www.etsy.com/listing/{1000 + index}/{shop_name.lower()}-{index}",
                shop_name=shop_name,
                price=22.0 + index * 2.5,
                currency=currency,
                rating=4.7,
                review_count=40 + index * 8,
                image_url=f"https://example.com/images/{shop_name.lower()}-{index}.jpg",
                description=f"{title} for modern minimalist home decor. Perfect printable wall art.",
                tags=tags[index - 1],
                detected_keywords=tags[index - 1],
                listing_source="user_shop",
                raw_data={"category": "Wall Art", "listing_source": "user_shop"},
            )
        )
    return listings


def _competitor_tags_for_query(query: str, shop_index: int, offset: int) -> List[str]:
    """Assign realistic repeated Etsy tags based on search query."""
    query_tags = {
        "minimalist wall art": [
            "minimalist wall art", "minimalist poster", "neutral wall art",
            "modern art print", "abstract poster", "line art print",
        ],
        "abstract beige print": [
            "abstract poster", "beige wall decor", "beige abstract poster",
            "neutral wall art", "abstract wall art", "modern art print",
        ],
        "scandinavian botanical poster": [
            "botanical print", "botanical wall art", "scandinavian print",
            "neutral botanical print", "botanical wall art", "nursery wall art",
        ],
        "neutral botanical print": [
            "neutral botanical print", "botanical print", "botanical wall art",
            "neutral wall art", "beige wall decor", "kitchen wall art",
        ],
        "gallery wall set": [
            "gallery wall set", "printable gallery wall set", "printable wall art",
            "modern art print", "neutral wall art", "instant download",
        ],
    }
    base = query_tags.get(query, [
        "wall art", "printable wall art", "modern art print",
        "neutral wall art", "abstract poster", "digital download",
    ])
    tag_pool = base + REALISTIC_ETSY_TAGS[(shop_index + offset) % len(REALISTIC_ETSY_TAGS):(shop_index + offset) % len(REALISTIC_ETSY_TAGS) + 3]
    seen = set()
    result = []
    for tag in tag_pool:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
        if len(result) >= 5:
            break
    return result


def mock_competitor_search_results(
    platform: str = "etsy",
    queries: List[str] | None = None,
    currency: str = "USD",
    exclude_shop: str = USER_SHOP,
) -> List[ProductListingSchema]:
    queries = queries or ["minimalist wall art", "abstract beige print"]
    listings: List[ProductListingSchema] = []
    listing_id = 2000
    position = 0

    for query_index, query in enumerate(queries):
        for shop_index, (shop_name, count, base_price) in enumerate(COMPETITOR_SHOPS):
            for offset in range(count):
                position += 1
                listing_id += 1
                title = f"{query.title()} — {shop_name} Collection #{offset + 1}"
                comp_tags = _competitor_tags_for_query(query, shop_index, offset)
                listings.append(
                    ProductListingSchema(
                        platform=platform,
                        title=title,
                        url=f"https://www.etsy.com/listing/{listing_id}/{shop_name.lower()}-{offset + 1}",
                        shop_name=shop_name,
                        price=round(base_price + offset * 2.2, 2),
                        currency=currency,
                        rating=4.3 + (offset % 3) * 0.2,
                        review_count=25 + offset * 11 + query_index * 3,
                        image_url=f"https://example.com/images/{shop_name.lower()}-{offset + 1}.jpg",
                        description=(
                            f"{title}. Features {comp_tags[0]} style. "
                            f"Instant download available. Perfect {query} for home decor."
                        ),
                        tags=comp_tags,
                        detected_keywords=comp_tags,
                        listing_source="competitor_search",
                        raw_data={
                            "matched_query": query,
                            "search_position": position - 1,
                            "category": "Wall Art",
                            "listing_source": "competitor_search",
                        },
                    )
                )

    if exclude_shop:
        exclude_key = exclude_shop.lower().replace("-", "").replace("_", "").replace(" ", "")
        listings = [
            listing for listing in listings
            if listing.shop_name.lower().replace("-", "").replace("_", "").replace(" ", "") != exclude_key
        ]
    return listings


def mock_shop_analysis_bundle(
    shop_name: str = USER_SHOP,
    platform: str = "etsy",
    currency: str = "USD",
) -> Tuple[List[ProductListingSchema], List[ProductListingSchema]]:
    user_listings = mock_user_shop_listings(shop_name=shop_name, platform=platform, currency=currency)
    queries = [
        "minimalist wall art",
        "abstract beige print",
        "scandinavian botanical poster",
        "neutral botanical print",
        "gallery wall set",
    ]
    competitor_listings = mock_competitor_search_results(
        platform=platform,
        queries=queries,
        currency=currency,
        exclude_shop=shop_name,
    )
    return user_listings, competitor_listings
