"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Shell } from "@/components/layout/shell";
import { OverviewCards } from "@/components/dashboard/overview-cards";
import { PricingChart } from "@/components/dashboard/pricing-chart";
import { KeywordCloud } from "@/components/dashboard/keyword-cloud";
import { CompetitorTable } from "@/components/dashboard/competitor-table";
import { ListingIssues } from "@/components/dashboard/listing-issues";
import { TrendsPanel } from "@/components/dashboard/trends-panel";
import { ListingTable } from "@/components/listings/listing-table";
import { AIRecommendations } from "@/components/ai/ai-recommendations";
import { FreeformSearch } from "@/components/ai/freeform-search";
import { getAnalysis } from "@/lib/api";
import type { AnalysisDetail } from "@/lib/types";
import { Loader2 } from "lucide-react";

export default function AnalysisPage() {
  const params = useParams();
  const id = Number(params.id);
  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getAnalysis(id)
      .then(setAnalysis)
      .catch(() => setError("Failed to load analysis. Is the backend running?"));
  }, [id]);

  if (error) {
    return (
      <Shell title="Analysis">
        <div className="text-center py-20 text-muted-foreground">{error}</div>
      </Shell>
    );
  }

  if (!analysis) {
    return (
      <Shell title="Loading...">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </Shell>
    );
  }

  return (
    <Shell title={`Analysis: ${analysis.input_value}`} dataSource={analysis.data_source}>
      <div className="space-y-6">
        {analysis.warning && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            {analysis.warning}
          </div>
        )}
        <OverviewCards analysis={analysis} />
        <PricingChart analysis={analysis} />
        <div className="grid gap-6 lg:grid-cols-2">
          <CompetitorTable competitors={analysis.competitors} />
          <KeywordCloud analysis={analysis} />
        </div>
        <TrendsPanel trends={analysis.trends} />
        <ListingIssues issues={analysis.listing_issues} />
        <ListingTable listings={analysis.listings} />
        <div className="grid gap-6 lg:grid-cols-2">
          <AIRecommendations analysisId={analysis.id} recommendations={analysis.recommendations} />
          <FreeformSearch analysisId={analysis.id} />
        </div>
      </div>
    </Shell>
  );
}
