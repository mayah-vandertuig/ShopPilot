"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";

export function KeywordCloud({ analysis }: { analysis: AnalysisDetail }) {
  const keywords = analysis.keyword_summary?.top_keywords || [];
  const tags = analysis.keyword_summary?.common_tags || [];
  const missing = analysis.keyword_summary?.missing_opportunities || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Keywords & Tags</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <p className="text-sm font-medium mb-3">Top Keywords</p>
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <span
                key={kw.keyword}
                className="rounded-full bg-primary/10 text-primary px-3 py-1 text-sm"
                style={{ fontSize: `${Math.min(12 + kw.count * 2, 18)}px` }}
              >
                {kw.keyword} ({kw.count})
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium mb-3">Common Tags</p>
          <div className="flex flex-wrap gap-2">
            {tags.map((t) => (
              <span key={t.tag} className="rounded-md bg-muted px-2 py-1 text-sm">{t.tag}</span>
            ))}
          </div>
        </div>
        {missing.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-3">Missing Opportunities</p>
            <div className="flex flex-wrap gap-2">
              {missing.map((m) => (
                <span key={m} className="rounded-md border border-dashed border-amber-300 bg-amber-50 px-2 py-1 text-sm text-amber-800">{m}</span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
