"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { generateRecommendations } from "@/lib/api";
import type { Recommendation } from "@/lib/types";
import { Sparkles, Loader2 } from "lucide-react";

export function AIRecommendations({
  analysisId,
  recommendations: initial,
}: {
  analysisId: number;
  recommendations: Recommendation[];
}) {
  const [recommendations, setRecommendations] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const result = await generateRecommendations(analysisId) as {
        recommendations?: Recommendation[];
        data_source?: string;
      };
      setRecommendations(result.recommendations || []);
      setDataSource(result.data_source ?? null);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Recommendations
        </CardTitle>
        <div className="flex items-center gap-2">
          {dataSource && <Badge variant={dataSource === "live" ? "success" : "warning"}>{dataSource}</Badge>}
          <Button onClick={handleGenerate} disabled={loading} size="sm">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Generate"}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {recommendations.map((rec, i) => (
          <div key={rec.id || i} className="rounded-lg border border-border p-4">
            <div className="flex items-center justify-between mb-2">
              <Badge>{rec.category}</Badge>
              <span className="text-xs text-muted-foreground">{Math.round(rec.confidence * 100)}% confidence</span>
            </div>
            <p className="font-medium text-sm">{rec.recommendation}</p>
            <p className="text-sm text-muted-foreground mt-1">{rec.reasoning}</p>
          </div>
        ))}
        {recommendations.length === 0 && (
          <p className="text-sm text-muted-foreground">Click Generate for AI-powered listing and expansion recommendations.</p>
        )}
      </CardContent>
    </Card>
  );
}
