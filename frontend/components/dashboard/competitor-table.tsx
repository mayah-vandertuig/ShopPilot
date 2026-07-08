"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import type { Competitor } from "@/lib/types";
import { Users, Trophy, ArrowRight, AlertTriangle } from "lucide-react";
import { normalizeShopName } from "@/lib/analysis-insights";

export function CompetitorCards({
  competitors,
  analysisId,
}: {
  competitors: Competitor[];
  analysisId: number;
}) {
  const top = competitors.slice(0, 3);
  if (!top.length) return null;

  return (
    <div className="grid gap-4 md:grid-cols-3 mb-6">
      {top.map((c, i) => (
        <Link
          key={c.id}
          href={`/analyses/${analysisId}/competitors/${c.id}`}
          className="rounded-xl border border-border bg-muted/30 p-4 hover:shadow-card-hover transition-shadow block"
        >
          <div className="flex items-center justify-between mb-3 gap-2">
            <p className="font-semibold text-foreground truncate">{c.competitor_name}</p>
            <div className="flex items-center gap-2 shrink-0">
              {i === 0 && (
                <Badge variant="default" className="gap-1">
                  <Trophy className="h-3 w-3" /> Top
                </Badge>
              )}
              <Badge variant="outline">{c.match_score.toFixed(0)} match</Badge>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-muted-foreground">Matched listings</p>
              <p className="text-sm font-semibold">{c.product_count}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Avg price</p>
              <p className="text-sm font-semibold">{formatCurrency(c.average_price)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Reviews</p>
              <p className="text-sm font-semibold">{c.total_reviews.toLocaleString()}</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-3 line-clamp-2">{c.positioning_summary}</p>
        </Link>
      ))}
    </div>
  );
}

export function CompetitorTable({
  competitors,
  analysisId,
  generatedQueries = [],
  warning,
}: {
  competitors: Competitor[];
  analysisId: number;
  generatedQueries?: string[];
  warning?: string;
  userShopName?: string;
}) {
  const userKey = userShopName ? normalizeShopName(userShopName) : "";
  const sorted = [...competitors]
    .filter((item) => !userKey || normalizeShopName(item.competitor_name) !== userKey)
    .sort((a, b) => b.match_score - a.match_score || b.product_count - a.product_count);
  const strongest = sorted[0];
  const avgCompetitorPrice =
    sorted.length > 0 ? sorted.reduce((sum, item) => sum + item.average_price, 0) / sorted.length : 0;
  const topKeyword = sorted.flatMap((item) => item.common_keywords ?? [])[0] || "—";

  return (
    <div className="space-y-6">
      {(warning) && (
        <div className="flex items-start gap-2 text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-xl p-4">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
          <span>{warning}</span>
        </div>
      )}

      {sorted.length > 0 && (
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard label="Discovered shops" value={String(sorted.length)} />
          <StatCard label="Strongest match" value={strongest?.competitor_name || "—"} />
          <StatCard label="Avg competitor price" value={formatCurrency(avgCompetitorPrice)} />
          <StatCard label="Top competitor keyword" value={topKeyword} />
        </div>
      )}

      <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-4 w-4 text-primary" />
          Discovered competitors
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Similar Etsy shops discovered from marketplace search results — not official marketplace competitor labels.
        </p>
      </CardHeader>
      <CardContent>
        {sorted.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No discovered competitors yet"
            description="Marketplace search did not return similar competitor shops. Your own shop is never shown here."
          >
            {generatedQueries.length > 0 && (
              <div className="mt-4 text-left max-w-xl mx-auto">
                <p className="text-sm font-medium text-foreground mb-2">Generated search queries</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {generatedQueries.map((query) => (
                    <li key={query}>• {query}</li>
                  ))}
                </ul>
              </div>
            )}
            {warning && (
              <div className="mt-4 flex items-start gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3 max-w-xl mx-auto text-left">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{warning}</span>
              </div>
            )}
          </EmptyState>
        ) : (
          <>
            <CompetitorCards competitors={sorted} analysisId={analysisId} />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="pb-3 pr-4 font-medium">Rank</th>
                    <th className="pb-3 pr-4 font-medium">Shop</th>
                    <th className="pb-3 pr-4 font-medium">Match</th>
                    <th className="pb-3 pr-4 font-medium">Matched listings</th>
                    <th className="pb-3 pr-4 font-medium">Avg price</th>
                    <th className="pb-3 pr-4 font-medium">Reviews</th>
                    <th className="pb-3 pr-4 font-medium">Tags / themes</th>
                    <th className="pb-3 pr-4 font-medium">Matched queries</th>
                    <th className="pb-3 font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((c, i) => (
                    <tr key={c.id} className="border-b border-border/80 hover:bg-muted/40">
                      <td className="py-3.5 pr-4 text-muted-foreground">#{i + 1}</td>
                      <td className="py-3.5 pr-4 font-medium text-foreground">{c.competitor_name}</td>
                      <td className="py-3.5 pr-4">
                        <Badge variant="outline">{c.match_score.toFixed(0)}</Badge>
                      </td>
                      <td className="py-3.5 pr-4">{c.product_count}</td>
                      <td className="py-3.5 pr-4">{formatCurrency(c.average_price)}</td>
                      <td className="py-3.5 pr-4">
                        {c.total_reviews.toLocaleString()}
                        {c.average_rating > 0 ? ` · ${c.average_rating.toFixed(1)}★` : ""}
                        <span className="block text-[11px] text-muted-foreground">across matched listings</span>
                      </td>
                      <td className="py-3.5 pr-4 text-muted-foreground">{(c.common_keywords ?? []).slice(0, 4).join(", ") || "—"}</td>
                      <td className="py-3.5 pr-4 text-muted-foreground">{(c.matched_queries ?? []).slice(0, 2).join(", ") || "—"}</td>
                      <td className="py-3.5">
                        <Link
                          href={`/analyses/${analysisId}/competitors/${c.id}`}
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          View <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-white p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold text-foreground mt-1 truncate">{value}</p>
    </div>
  );
}
