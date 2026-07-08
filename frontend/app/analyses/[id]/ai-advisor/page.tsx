"use client";

import { useEffect, useState } from "react";
import { AIRecommendations } from "@/components/ai/ai-recommendations";
import { FreeformSearch } from "@/components/ai/freeform-search";
import { PageIntro } from "@/components/layout/page-intro";
import { ErrorState } from "@/components/ui/error-state";
import { Badge } from "@/components/ui/badge";
import { getSettingsStatus } from "@/lib/api";
import { useAnalysis } from "@/lib/analysis-context";
import { getUserListings } from "@/lib/analysis-insights";
import type { SettingsStatus } from "@/lib/types";
import { Bot } from "lucide-react";

export default function AIAdvisorPage() {
  const { analysis } = useAnalysis();
  const [settings, setSettings] = useState<SettingsStatus | null>(null);
  const hasListings = getUserListings(analysis).length > 0;
  const userListingCount = getUserListings(analysis).length;
  const competitorCount = analysis.competitors.length;

  useEffect(() => {
    getSettingsStatus()
      .then(setSettings)
      .catch(() => setSettings(null));
  }, []);

  return (
    <div className="space-y-6">
      <PageIntro
        title="AI Advisor"
        description="Actionable recommendations and free-form market questions grounded in your Etsy shop analysis."
      />

      <div className="dashboard-card p-4 flex flex-wrap items-center gap-3">
        <Bot className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium text-foreground">OpenAI status</span>
        <Badge variant={settings?.openai_configured ? "success" : "warning"}>
          {settings?.openai_configured ? "Configured" : "Disabled — no API key"}
        </Badge>
        {!settings?.openai_configured && (
          <span className="text-sm text-muted-foreground">
            Add OPENAI_API_KEY to enable live AI recommendations. Mock expansion ideas are still available from analysis.
          </span>
        )}
      </div>

      {!hasListings ? (
        <ErrorState
          title="No listing data yet"
          message="The AI advisor needs scraped products from your Etsy shop. Enter a shop name on the dashboard, then return here once listings are collected."
        />
      ) : (
        <>
          <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            <span className="rounded-full border border-border bg-white px-3 py-1">
              Shop: {analysis.input_value}
            </span>
            <span className="rounded-full border border-border bg-white px-3 py-1">
              {userListingCount} your listing{userListingCount === 1 ? "" : "s"}
            </span>
            <span className="rounded-full border border-border bg-white px-3 py-1">
              {competitorCount} discovered competitor{competitorCount === 1 ? "" : "s"}
            </span>
            {analysis.pricing_summary?.average_price ? (
              <span className="rounded-full border border-border bg-white px-3 py-1">
                Avg price ${analysis.pricing_summary.average_price.toFixed(2)}
              </span>
            ) : null}
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <AIRecommendations
              analysisId={analysis.id}
              recommendations={analysis.recommendations}
              disabled={!settings?.openai_configured}
            />
            <FreeformSearch analysisId={analysis.id} disabled={!settings?.openai_configured} />
          </div>
        </>
      )}
    </div>
  );
}
