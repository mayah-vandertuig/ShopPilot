"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { generateRecommendations } from "@/lib/api";
import type { Recommendation } from "@/lib/types";
import { Sparkles, Loader2, Tag, DollarSign, Type, Package, ArrowRight } from "lucide-react";

const categoryMeta: Record<string, { icon: React.ComponentType<{ className?: string }>; label: string }> = {
  title: { icon: Type, label: "Improved title" },
  tags: { icon: Tag, label: "Suggested tags" },
  pricing: { icon: DollarSign, label: "Pricing recommendation" },
  positioning: { icon: Sparkles, label: "Positioning" },
  product_expansion: { icon: Package, label: "Product expansion" },
  listing: { icon: Sparkles, label: "Listing advice" },
  general: { icon: Sparkles, label: "Recommendation" },
};

export function AIRecommendations({
  analysisId,
  recommendations: initial,
}: {
  analysisId: number;
  recommendations: Recommendation[];
}) {
  const [recommendations, setRecommendations] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateRecommendations(analysisId) as { recommendations?: Recommendation[] };
      setRecommendations(result.recommendations || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate recommendations");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            AI recommendations
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Grounded suggestions from your collected market data.</p>
        </div>
        <Button onClick={handleGenerate} disabled={loading} size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Generate"}
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && <div className="alert-danger">{error}</div>}
        {recommendations.map((rec, i) => {
          const meta = categoryMeta[rec.category] || categoryMeta.general;
          const Icon = meta.icon;
          return (
            <div key={rec.id || i} className="group rounded-xl border border-border bg-white p-5 hover:shadow-card-hover transition-all">
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{meta.label}</p>
                    <Badge variant="outline" className="mt-1">{rec.category}</Badge>
                  </div>
                </div>
                <span className="text-xs font-medium text-muted-foreground">{Math.round(rec.confidence * 100)}% confidence</span>
              </div>
              <p className="text-sm font-medium text-foreground leading-relaxed">{rec.recommendation}</p>
              <p className="text-sm text-muted-foreground mt-2">{rec.reasoning}</p>
              <div className="flex items-center gap-1 mt-4 text-xs font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                Action insight <ArrowRight className="h-3 w-3" />
              </div>
            </div>
          );
        })}
        {recommendations.length === 0 && !error && (
          <p className="text-sm text-muted-foreground text-center py-8">
            Click Generate for AI-powered title, tag, pricing, and expansion recommendations.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
