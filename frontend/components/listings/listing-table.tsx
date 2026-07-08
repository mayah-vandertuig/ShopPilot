"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import type { Listing, ListingIssue } from "@/lib/types";
import { List } from "lucide-react";
import { ListingDetail } from "./listing-detail";

export function ListingTable({
  listings,
  issues = [],
}: {
  listings: Listing[];
  issues?: ListingIssue[];
}) {
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Listing | null>(null);

  const issueCountByListing = useMemo(() => {
    const map = new Map<number, number>();
    issues.forEach((issue) => {
      if (issue.listing_id) map.set(issue.listing_id, (map.get(issue.listing_id) || 0) + 1);
    });
    return map;
  }, [issues]);

  const filtered = listings.filter(
    (l) =>
      l.title.toLowerCase().includes(filter.toLowerCase()) ||
      l.shop_name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <>
      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="flex items-center gap-2">
            <List className="h-4 w-4 text-primary" />
            All listings ({listings.length})
          </CardTitle>
          <Input
            placeholder="Filter by title or shop..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="max-w-xs"
          />
        </CardHeader>
        <CardContent>
          {listings.length === 0 ? (
            <EmptyState icon={List} title="No listings collected" description="Listings appear here after a successful marketplace analysis." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="pb-3 pr-3 font-medium w-14"></th>
                    <th className="pb-3 pr-4 font-medium">Title</th>
                    <th className="pb-3 pr-4 font-medium">Shop</th>
                    <th className="pb-3 pr-4 font-medium">Price</th>
                    <th className="pb-3 pr-4 font-medium">Rating</th>
                    <th className="pb-3 pr-4 font-medium">Reviews</th>
                    <th className="pb-3 pr-4 font-medium">Tags</th>
                    <th className="pb-3 font-medium">Issues</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((l) => (
                    <tr
                      key={l.id}
                      className="border-b border-border/80 cursor-pointer hover:bg-muted/40 transition-colors"
                      onClick={() => setSelected(l)}
                    >
                      <td className="py-3 pr-3">
                        {l.image_url ? (
                          <img src={l.image_url} alt="" className="h-10 w-10 rounded-lg object-cover border border-border" />
                        ) : (
                          <div className="h-10 w-10 rounded-lg bg-muted border border-border" />
                        )}
                      </td>
                      <td className="py-3 pr-4 max-w-xs font-medium text-foreground truncate">{l.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground">{l.shop_name}</td>
                      <td className="py-3 pr-4 font-medium">{formatCurrency(l.price, l.currency)}</td>
                      <td className="py-3 pr-4">{l.rating > 0 ? l.rating.toFixed(1) : "—"}</td>
                      <td className="py-3 pr-4">{l.review_count || "—"}</td>
                      <td className="py-3 pr-4 max-w-[140px] truncate text-muted-foreground">{l.tags.slice(0, 3).join(", ")}</td>
                      <td className="py-3">
                        {(issueCountByListing.get(l.id) || 0) > 0 ? (
                          <Badge variant="warning">{issueCountByListing.get(l.id)}</Badge>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      {selected && <ListingDetail listing={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
