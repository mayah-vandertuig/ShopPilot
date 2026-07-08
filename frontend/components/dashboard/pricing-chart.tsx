"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import type { AnalysisDetail } from "@/lib/types";
import { BarChart3, DollarSign } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export function PricingChart({ analysis }: { analysis: AnalysisDetail }) {
  const pricing = analysis.pricing_summary;
  const buckets: Record<string, number> = {};
  analysis.listings.forEach((l) => {
    if (l.price > 0) {
      const bucket = `${Math.floor(l.price / 10) * 10}`;
      buckets[bucket] = (buckets[bucket] || 0) + 1;
    }
  });
  const data = Object.entries(buckets)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([range, count]) => ({ range: `$${range}`, count }));

  const stats = [
    { label: "Min", value: pricing?.min_price },
    { label: "Median", value: pricing?.median_price },
    { label: "Average", value: pricing?.average_price },
    { label: "Max", value: pricing?.max_price },
  ];

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-primary" />
            Price analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {stats.map((s) => (
              <div key={s.label} className="rounded-xl border border-border bg-muted/50 p-4 text-center">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{s.label}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{formatCurrency(s.value || 0, analysis.currency)}</p>
              </div>
            ))}
          </div>

          {data.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
                  <XAxis dataKey="range" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: "#F1F5F9" }}
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      border: "1px solid #E5E7EB",
                      borderRadius: "0.75rem",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.08)",
                      color: "#0F172A",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="count" fill="#2563EB" radius={[6, 6, 0, 0]} maxBarSize={48} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState icon={BarChart3} title="No pricing data" description="No priced listings were found in this analysis." />
          )}

          <div className="grid gap-6 lg:grid-cols-2 mt-8">
            <div>
              <p className="text-sm font-semibold text-foreground mb-3">Underpriced listings</p>
              {(pricing?.underpriced?.length || 0) > 0 ? (
                <ul className="space-y-2">
                  {pricing?.underpriced?.map((l, i) => (
                    <li key={i} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                      <span className="truncate pr-3 text-foreground">{l.title}</span>
                      <span className="font-medium text-success shrink-0">{formatCurrency(l.price, analysis.currency)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No underpriced listings detected.</p>
              )}
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground mb-3">Overpriced listings</p>
              {(pricing?.overpriced?.length || 0) > 0 ? (
                <ul className="space-y-2">
                  {pricing?.overpriced?.map((l, i) => (
                    <li key={i} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                      <span className="truncate pr-3 text-foreground">{l.title}</span>
                      <span className="font-medium text-warning shrink-0">{formatCurrency(l.price, analysis.currency)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No overpriced listings detected.</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
