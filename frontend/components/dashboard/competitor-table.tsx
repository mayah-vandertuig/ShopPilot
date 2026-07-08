"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import type { Competitor } from "@/lib/types";
import { Users, Trophy } from "lucide-react";

export function CompetitorCards({ competitors }: { competitors: Competitor[] }) {
  const top = competitors.slice(0, 3);
  if (!top.length) return null;

  return (
    <div className="grid gap-4 md:grid-cols-3 mb-6">
      {top.map((c, i) => (
        <div key={c.id} className="rounded-xl border border-border bg-muted/30 p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="font-semibold text-foreground truncate">{c.competitor_name}</p>
            {i === 0 && (
              <Badge variant="default" className="gap-1">
                <Trophy className="h-3 w-3" /> Top
              </Badge>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-muted-foreground">Products</p>
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
        </div>
      ))}
    </div>
  );
}

export function CompetitorTable({ competitors }: { competitors: Competitor[] }) {
  return (
    <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-4 w-4 text-primary" />
            Competitor ranking
          </CardTitle>
        </CardHeader>
        <CardContent>
          {competitors.length === 0 ? (
            <EmptyState icon={Users} title="No competitors found" description="Competitor insights appear once listings with shop names are collected." />
          ) : (
            <>
              <CompetitorCards competitors={competitors} />
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-muted-foreground">
                      <th className="pb-3 pr-4 font-medium">Rank</th>
                      <th className="pb-3 pr-4 font-medium">Shop</th>
                      <th className="pb-3 pr-4 font-medium">Products</th>
                      <th className="pb-3 pr-4 font-medium">Avg price</th>
                      <th className="pb-3 pr-4 font-medium">Reviews</th>
                      <th className="pb-3 font-medium">Keywords</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competitors.map((c, i) => (
                      <tr key={c.id} className="border-b border-border/80 hover:bg-muted/40">
                        <td className="py-3.5 pr-4 text-muted-foreground">#{i + 1}</td>
                        <td className="py-3.5 pr-4 font-medium text-foreground">{c.competitor_name}</td>
                        <td className="py-3.5 pr-4">{c.product_count}</td>
                        <td className="py-3.5 pr-4">{formatCurrency(c.average_price)}</td>
                        <td className="py-3.5 pr-4">{c.total_reviews.toLocaleString()}</td>
                        <td className="py-3.5 text-muted-foreground">{c.common_keywords.slice(0, 4).join(", ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
  );
}
