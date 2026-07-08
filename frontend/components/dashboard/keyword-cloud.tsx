"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import type { AnalysisDetail } from "@/lib/types";
import { Hash, BarChart3 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export function KeywordCloud({ analysis }: { analysis: AnalysisDetail }) {
  const keywords = analysis.keyword_summary?.top_keywords || [];
  const tags = analysis.keyword_summary?.common_tags || [];
  const missing = analysis.keyword_summary?.missing_opportunities || [];
  const chartData = keywords.slice(0, 10).map((k) => ({ keyword: k.keyword, count: k.count }));

  return (
    <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-4 w-4 text-primary" />
              Top keywords & tags
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {keywords.length === 0 ? (
              <EmptyState icon={Hash} title="No keywords extracted" description="Keywords appear once listing titles and tags are analyzed." />
            ) : (
              <>
                <div>
                  <p className="text-sm font-medium text-foreground mb-3">Top keywords</p>
                  <div className="flex flex-wrap gap-2">
                    {keywords.map((kw) => (
                      <span key={kw.keyword} className="rounded-full bg-primary/10 text-primary px-3 py-1 text-sm font-medium">
                        {kw.keyword} <span className="text-primary/70">({kw.count})</span>
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground mb-3">Common tags</p>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((t) => (
                      <span key={t.tag} className="rounded-lg border border-border bg-muted/50 px-2.5 py-1 text-sm text-foreground">
                        {t.tag}
                      </span>
                    ))}
                  </div>
                </div>
                {missing.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-foreground mb-3">Missing opportunities</p>
                    <div className="flex flex-wrap gap-2">
                      {missing.map((m) => (
                        <span key={m} className="rounded-lg border border-dashed border-amber-300 bg-amber-50 px-2.5 py-1 text-sm text-amber-900">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              Keyword frequency
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                    <YAxis dataKey="keyword" type="category" width={100} tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#FFFFFF",
                        border: "1px solid #E5E7EB",
                        borderRadius: "0.75rem",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState icon={BarChart3} title="No frequency data" description="Keyword frequency chart populates from extracted title terms." />
            )}
          </CardContent>
        </Card>
    </div>
  );
}
