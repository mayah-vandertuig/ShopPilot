"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Trend } from "@/lib/types";

export function TrendsPanel({ trends }: { trends: Trend[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Market Trends</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2">
          {trends.map((trend) => (
            <div key={trend.id} className="rounded-lg border border-border p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{trend.trend_name}</h4>
                <span className="text-xs bg-muted px-2 py-1 rounded">{trend.trend_type}</span>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{trend.evidence}</p>
              <p className="text-sm">{trend.opportunity}</p>
            </div>
          ))}
        </div>
        {trends.length === 0 && <p className="text-muted-foreground text-sm">No trends detected yet.</p>}
      </CardContent>
    </Card>
  );
}
