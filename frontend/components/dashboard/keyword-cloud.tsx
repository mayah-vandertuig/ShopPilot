"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import type { AnalysisDetail } from "@/lib/types";
import { Hash, BarChart3, Lightbulb } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export function KeywordCloud({ analysis }: { analysis: AnalysisDetail }) {
  const keywords = analysis.keyword_summary?.top_keywords || [];
  const competitorKeywords = analysis.keyword_summary?.competitor_keywords || [];
  const tags = analysis.keyword_summary?.common_tags || [];
  const missing = analysis.keyword_summary?.missing_opportunities || [];
  const clusters = analysis.keyword_summary?.keyword_clusters || [];
  const actions = analysis.keyword_summary?.suggested_actions || [];
  const chartData = keywords.slice(0, 10).map((item) => ({ keyword: item.keyword, count: item.count }));

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-4 w-4 text-primary" />
              Your shop keywords
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {keywords.length === 0 ? (
              <EmptyState icon={Hash} title="No keywords extracted" description="Keywords appear once listing titles and tags are analyzed." />
            ) : (
              <>
                <KeywordGroup title="Top keywords" items={keywords.map((item) => `${item.keyword} (${item.count})`)} tone="primary" />
                <KeywordGroup title="Common Etsy tags" items={tags.map((item) => item.tag)} />
                {missing.length > 0 && (
                  <KeywordGroup title="Missing keyword opportunities" items={missing} tone="warning" />
                )}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              Competitor keywords
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {competitorKeywords.length > 0 ? (
              <KeywordGroup
                title="Top competitor terms"
                items={competitorKeywords.slice(0, 12).map((item) => `${item.keyword} (${item.count})`)}
              />
            ) : (
              <EmptyState icon={BarChart3} title="No competitor keyword data" description="Competitor keywords populate when similar shops are discovered." />
            )}
            {chartData.length > 0 && (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                    <YAxis dataKey="keyword" type="category" width={100} tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {clusters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Keyword clusters</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {clusters.map((cluster) => (
              <div key={cluster.name} className="rounded-xl border border-border bg-muted/20 p-4">
                <p className="text-sm font-semibold text-foreground">{cluster.name}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {cluster.keywords.map((keyword) => (
                    <span key={keyword} className="rounded-full border border-border bg-white px-2.5 py-1 text-xs text-muted-foreground">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {actions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              Suggested actions for titles, tags, and descriptions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {actions.map((action) => (
                <li key={action}>• {action}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function KeywordGroup({
  title,
  items,
  tone = "default",
}: {
  title: string;
  items: string[];
  tone?: "default" | "primary" | "warning";
}) {
  return (
    <div>
      <p className="text-sm font-medium text-foreground mb-3">{title}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className={
              tone === "primary"
                ? "rounded-full bg-primary/10 text-primary px-3 py-1 text-sm font-medium"
                : tone === "warning"
                  ? "rounded-lg border border-dashed border-amber-300 bg-amber-50 px-2.5 py-1 text-sm text-amber-900"
                  : "rounded-lg border border-border bg-muted/50 px-2.5 py-1 text-sm text-foreground"
            }
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
