import type { AnalysisDetail, Competitor, Listing } from "./types";

const USER_SOURCES = new Set(["user", "user_shop"]);
const COMPETITOR_SOURCES = new Set(["competitor", "competitor_search"]);

export function normalizeShopName(name: string): string {
  return name.toLowerCase().replace(/[\s_\-]+/g, "").trim();
}

export function isUserShopListing(listing: Listing): boolean {
  const source = listing.listing_source || "user_shop";
  return USER_SOURCES.has(source);
}

export function isCompetitorSearchListing(listing: Listing): boolean {
  return COMPETITOR_SOURCES.has(listing.listing_source || "");
}

export function getUserListings(analysis: AnalysisDetail) {
  return analysis.listings.filter(isUserShopListing);
}

export function getCompetitorListings(analysis: AnalysisDetail) {
  return analysis.listings.filter(isCompetitorSearchListing);
}

export function filterDiscoveredCompetitors(analysis: AnalysisDetail): Competitor[] {
  const userKey = normalizeShopName(analysis.input_value);
  return (analysis.competitors ?? []).filter(
    (competitor) => normalizeShopName(competitor.competitor_name) !== userKey
  );
}

export function getStrongestCompetitor(analysis: AnalysisDetail) {
  const competitors = filterDiscoveredCompetitors(analysis);
  if (!competitors.length) return null;
  return [...competitors].sort((a, b) => b.match_score - a.match_score)[0];
}

export function getDetectedNiche(analysis: AnalysisDetail) {
  const clusters = analysis.keyword_summary?.keyword_clusters || [];
  if (clusters.length > 0) {
    const keywords = clusters.flatMap((cluster) => cluster.keywords).slice(0, 3);
    return keywords.join(" · ") || "General marketplace";
  }
  const top = analysis.keyword_summary?.top_keywords?.[0]?.keyword;
  return top ? `${top} niche` : "General marketplace";
}

export function getTopProductThemes(analysis: AnalysisDetail) {
  const insights = analysis.keyword_summary?.tag_insights || [];
  if (insights.length > 0) {
    return insights.slice(0, 3).map((item) => item.tag);
  }
  return (analysis.keyword_summary?.top_keywords || []).slice(0, 3).map((item) => item.keyword);
}

export function getMainOpportunity(analysis: AnalysisDetail) {
  if (analysis.recommendations[0]?.recommendation) return analysis.recommendations[0].recommendation;
  const topTag = analysis.keyword_summary?.summary_stats?.top_opportunity_tag;
  if (topTag) return `Add or expand tags like "${topTag}" — highest opportunity score in your niche.`;
  const missing = analysis.keyword_summary?.missing_opportunities?.[0];
  if (missing) return `Add listings or tags targeting "${missing}" to close a competitor keyword gap.`;
  return "Review tag opportunities and competitor positioning on the Keyword & Tag Intelligence page.";
}

export function getRecommendedActions(analysis: AnalysisDetail) {
  const actions = [
    ...(analysis.keyword_summary?.suggested_actions || []),
    ...analysis.recommendations.slice(0, 2).map((rec) => rec.recommendation),
  ];
  return [...new Set(actions)].slice(0, 4);
}
