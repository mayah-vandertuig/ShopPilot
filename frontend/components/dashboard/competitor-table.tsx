"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import type { Competitor } from "@/lib/types";

export function CompetitorTable({ competitors }: { competitors: Competitor[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Competitor Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-muted-foreground">
                <th className="pb-3 font-medium">Shop</th>
                <th className="pb-3 font-medium">Products</th>
                <th className="pb-3 font-medium">Avg Price</th>
                <th className="pb-3 font-medium">Reviews</th>
                <th className="pb-3 font-medium">Keywords</th>
                <th className="pb-3 font-medium">Positioning</th>
              </tr>
            </thead>
            <tbody>
              {competitors.map((c, i) => (
                <tr key={c.id} className="border-b border-border/50">
                  <td className="py-3 font-medium">
                    <span className="inline-flex items-center gap-2">
                      {i === 0 && <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">#1</span>}
                      {c.competitor_name}
                    </span>
                  </td>
                  <td className="py-3">{c.product_count}</td>
                  <td className="py-3">{formatCurrency(c.average_price)}</td>
                  <td className="py-3">{c.total_reviews.toLocaleString()}</td>
                  <td className="py-3">{c.common_keywords.slice(0, 3).join(", ")}</td>
                  <td className="py-3 text-muted-foreground max-w-xs truncate">{c.positioning_summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
