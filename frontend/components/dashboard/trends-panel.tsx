"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import type { Trend } from "@/lib/types";
import { TrendingUp } from "lucide-react";

export function TrendsPanel({ trends }: { trends: Trend[] }) {
  return (
    <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Market trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          {trends.length === 0 ? (
            <EmptyState icon={TrendingUp} title="No trends detected" description="Trends emerge when repeated themes appear across multiple listings." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {trends.map((trend) => (
                <div key={trend.id} className="rounded-xl border border-border bg-white p-5 hover:shadow-card-hover transition-shadow">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h4 className="font-semibold text-foreground">{trend.trend_name}</h4>
                    <Badge variant="outline">{trend.trend_type}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{trend.evidence}</p>
                  <p className="text-sm text-foreground">{trend.opportunity}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
  );
}
