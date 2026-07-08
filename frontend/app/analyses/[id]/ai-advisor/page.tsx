"use client";

import { AIRecommendations } from "@/components/ai/ai-recommendations";
import { FreeformSearch } from "@/components/ai/freeform-search";
import { PageIntro } from "@/components/layout/page-intro";
import { ErrorState } from "@/components/ui/error-state";
import { useAnalysis } from "@/lib/analysis-context";

export default function AIAdvisorPage() {
  const { analysis } = useAnalysis();
  const hasListings = analysis.listings.length > 0;
  const listingCount = analysis.listings.length;
  const competitorCount = analysis.competitors.length;

  return (
    <div className="space-y-6">
      <PageIntro
        title="AI Advisor"
        description="Actionable recommendations and free-form market questions grounded in your analysis."
      />

      {!hasListings ? (
        <ErrorState
          title="No listing data yet"
          message="The AI advisor needs scraped products from your analysis. Run a new Etsy shop analysis from the dashboard, then return here once listings are collected."
        />
      ) : (
        <>
          <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            <span className="rounded-full border border-border bg-white px-3 py-1">
              {listingCount} listing{listingCount === 1 ? "" : "s"}
            </span>
            <span className="rounded-full border border-border bg-white px-3 py-1">
              {competitorCount} competitor{competitorCount === 1 ? "" : "s"}
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
            />
            <FreeformSearch analysisId={analysis.id} />
          </div>
        </>
      )}
    </div>
  );
}
