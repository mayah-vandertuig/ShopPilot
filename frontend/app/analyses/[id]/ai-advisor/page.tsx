"use client";

import { AIRecommendations } from "@/components/ai/ai-recommendations";
import { FreeformSearch } from "@/components/ai/freeform-search";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function AIAdvisorPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="AI Advisor" description="Actionable recommendations and free-form market questions grounded in your analysis." />
      <div className="grid gap-6 xl:grid-cols-2">
        <AIRecommendations analysisId={analysis.id} recommendations={analysis.recommendations} />
        <FreeformSearch analysisId={analysis.id} />
      </div>
    </div>
  );
}
