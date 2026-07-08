"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import type { AnalysisDetail } from "@/lib/types";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export function PricingChart({ analysis }: { analysis: AnalysisDetail }) {
  const pricing = analysis.pricing_summary;
  const buckets: Record<string, number> = {};
  analysis.listings.forEach((l) => {
    if (l.price > 0) {
      const bucket = `${Math.floor(l.price / 10) * 10}-${Math.floor(l.price / 10) * 10 + 10}`;
      buckets[bucket] = (buckets[bucket] || 0) + 1;
    }
  });
  const data = Object.entries(buckets).map(([range, count]) => ({ range: `$${range}`, count }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pricing Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Min", value: pricing?.min_price },
            { label: "Median", value: pricing?.median_price },
            { label: "Average", value: pricing?.average_price },
            { label: "Max", value: pricing?.max_price },
          ].map((s) => (
            <div key={s.label} className="rounded-lg bg-muted p-4 text-center">
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <p className="text-xl font-bold">{formatCurrency(s.value || 0)}</p>
            </div>
          ))}
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(221 83% 53%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {(pricing?.underpriced?.length || 0) > 0 && (
          <div className="mt-4">
            <p className="text-sm font-medium mb-2">Underpriced Listings</p>
            <ul className="text-sm text-muted-foreground space-y-1">
              {pricing?.underpriced?.slice(0, 3).map((l, i) => (
                <li key={i}>{l.title.slice(0, 50)} — {formatCurrency(l.price)}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
