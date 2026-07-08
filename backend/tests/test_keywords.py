from app.analysis.keywords import extract_keywords, _tokenize
from app.schemas import ProductListingSchema


def test_tokenize_removes_stopwords():
  words = _tokenize("the minimalist wall art print")
  assert "the" not in words
  assert "minimalist" in words


def test_extract_keywords():
  listings = [
    ProductListingSchema(platform="etsy", title="Minimalist Abstract Canvas", tags=["minimalist", "abstract"]),
    ProductListingSchema(platform="etsy", title="Minimalist Line Art Print", tags=["line art"]),
  ]
  summary = extract_keywords(listings)
  assert any(k["keyword"] == "minimalist" for k in summary.top_keywords)
