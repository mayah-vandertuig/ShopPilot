"use client";

import { useMemo, useState, useEffect, useCallback } from "react";
import { usePathname } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import type { Listing, ListingIssue } from "@/lib/types";
import { isCompetitorSearchListing, isUserShopListing } from "@/lib/analysis-insights";
import { List } from "lucide-react";
import { ListingDetail } from "./listing-detail";

type SourceFilter = "all" | "user" | "competitor";
type SeverityFilter = "all" | "high" | "medium" | "low";

export function ListingTable({
  listings,
  issues = [],
  recommendations = [],
  userShopName,
}: {
  listings: Listing[];
  issues?: ListingIssue[];
  recommendations?: Array<{ listing_id: number | null; recommendation: string; category: string }>;
  userShopName?: string;
}) {
  const [filter, setFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState<SourceFilter>("all");
  const [shopFilter, setShopFilter] = useState("all");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [keywordFilter, setKeywordFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("all");
  const [selected, setSelected] = useState<Listing | null>(null);
  const pathname = usePathname();
  const closeDetail = useCallback(() => setSelected(null), []);

  useEffect(() => {
    setSelected(null);
  }, [pathname]);

  const issueCountByListing = useMemo(() => {
    const map = new Map<number, number>();
    issues.forEach((issue) => {
      if (issue.listing_id) map.set(issue.listing_id, (map.get(issue.listing_id) || 0) + 1);
    });
    return map;
  }, [issues]);

  const issueSeverityByListing = useMemo(() => {
    const map = new Map<number, string>();
    const rank = { high: 3, medium: 2, low: 1 };
    issues.forEach((issue) => {
      if (!issue.listing_id) return;
      const current = map.get(issue.listing_id);
      if (!current || rank[issue.severity] > rank[current as keyof typeof rank]) {
        map.set(issue.listing_id, issue.severity);
      }
    });
    return map;
  }, [issues]);

  const shopNames = useMemo(
    () => [...new Set(listings.map((listing) => listing.shop_name).filter(Boolean))].sort(),
    [listings]
  );

  const filtered = listings.filter((listing) => {
    const text = `${listing.title} ${listing.shop_name} ${listing.tags.join(" ")}`.toLowerCase();
    const matchesText = text.includes(filter.toLowerCase());
    const matchesSource =
      sourceFilter === "all" ||
      (sourceFilter === "user" && isUserShopListing(listing)) ||
      (sourceFilter === "competitor" && isCompetitorSearchListing(listing));
    const matchesShop = shopFilter === "all" || listing.shop_name === shopFilter;
    const matchesMin = !minPrice || listing.price >= Number(minPrice);
    const matchesMax = !maxPrice || listing.price <= Number(maxPrice);
    const matchesKeyword = !keywordFilter || text.includes(keywordFilter.toLowerCase());
    const severity = issueSeverityByListing.get(listing.id);
    const matchesSeverity =
      severityFilter === "all" || severity === severityFilter || (!severity && severityFilter === "low");
    return matchesText && matchesSource && matchesShop && matchesMin && matchesMax && matchesKeyword && matchesSeverity;
  });

  const selectedIssues = selected ? issues.filter((issue) => issue.listing_id === selected.id) : [];
  const selectedRecommendations = selected
    ? recommendations.filter((rec) => rec.listing_id === selected.id || rec.listing_id === null).slice(0, 3)
    : [];

  return (
    <>
      <Card>
        <CardHeader className="space-y-4">
          <CardTitle className="flex items-center gap-2">
            <List className="h-4 w-4 text-primary" />
            All listings ({listings.length})
          </CardTitle>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Input placeholder="Search title or shop..." value={filter} onChange={(e) => setFilter(e.target.value)} />
            <Select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value as SourceFilter)}>
              <option value="all">All sources</option>
              <option value="user">Your listings</option>
              <option value="competitor">Competitor listings</option>
            </Select>
            <Select value={shopFilter} onChange={(e) => setShopFilter(e.target.value)}>
              <option value="all">All shops</option>
              {shopNames.map((shop) => (
                <option key={shop} value={shop}>{shop}</option>
              ))}
            </Select>
            <Select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value as SeverityFilter)}>
              <option value="all">All issue severities</option>
              <option value="high">High issues</option>
              <option value="medium">Medium issues</option>
              <option value="low">Low / no issues</option>
            </Select>
            <Input placeholder="Min price" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} />
            <Input placeholder="Max price" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
            <Input placeholder="Keyword filter" value={keywordFilter} onChange={(e) => setKeywordFilter(e.target.value)} />
          </div>
        </CardHeader>
        <CardContent>
          {listings.length === 0 ? (
            <EmptyState icon={List} title="No listings collected" description="Listings appear here after a successful Etsy shop analysis." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="pb-3 pr-3 font-medium w-14"></th>
                    <th className="pb-3 pr-4 font-medium">Title</th>
                    <th className="pb-3 pr-4 font-medium">Shop</th>
                    <th className="pb-3 pr-4 font-medium">Platform</th>
                    <th className="pb-3 pr-4 font-medium">Price</th>
                    <th className="pb-3 pr-4 font-medium">Rating</th>
                    <th className="pb-3 pr-4 font-medium">Reviews</th>
                    <th className="pb-3 pr-4 font-medium">Tags / keywords</th>
                    <th className="pb-3 pr-4 font-medium">Issues</th>
                    <th className="pb-3 font-medium">Source</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((listing) => (
                    <tr
                      key={listing.id}
                      className="border-b border-border/80 cursor-pointer hover:bg-muted/40 transition-colors"
                      onClick={() => setSelected(listing)}
                    >
                      <td className="py-3 pr-3">
                        {listing.image_url ? (
                          <img src={listing.image_url} alt="" className="h-10 w-10 rounded-lg object-cover border border-border" />
                        ) : (
                          <div className="h-10 w-10 rounded-lg bg-muted border border-border" />
                        )}
                      </td>
                      <td className="py-3 pr-4 max-w-xs font-medium text-foreground truncate">{listing.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground">{listing.shop_name}</td>
                      <td className="py-3 pr-4 text-muted-foreground">{listing.platform}</td>
                      <td className="py-3 pr-4 font-medium">{formatCurrency(listing.price, listing.currency)}</td>
                      <td className="py-3 pr-4">{listing.rating > 0 ? listing.rating.toFixed(1) : "—"}</td>
                      <td className="py-3 pr-4">{listing.review_count || "—"}</td>
                      <td className="py-3 pr-4 max-w-[160px] truncate text-muted-foreground">
                        {[...listing.tags, ...listing.detected_keywords].slice(0, 3).join(", ") || "—"}
                      </td>
                      <td className="py-3 pr-4">
                        {(issueCountByListing.get(listing.id) || 0) > 0 ? (
                          <Badge variant="warning">{issueCountByListing.get(listing.id)}</Badge>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="py-3">
                        <Badge variant={isUserShopListing(listing) ? "success" : "outline"}>
                          {isUserShopListing(listing) ? "Your shop" : "Competitor search"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      {selected && (
        <ListingDetail
          listing={selected}
          issues={selectedIssues}
          recommendations={selectedRecommendations}
          isUserListing={isUserShopListing(selected) || selected.shop_name === userShopName}
          onClose={closeDetail}
        />
      )}
    </>
  );
}
