"use client";

import { CompetitorTable } from "@/components/dashboard/competitor-table";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";
import { filterDiscoveredCompetitors } from "@/lib/analysis-insights";

export default function CompetitorsPage() {
  const { analysis } = useAnalysis();
  const competitors = filterDiscoveredCompetitors(analysis);

  return (
    <div className="space-y-6">
      <PageIntro
        title="Discovered competitors"
        description="Similar shops inferred from your catalog themes and marketplace search results."
      />
      <CompetitorTable
        competitors={competitors}
        analysisId={analysis.id}
        generatedQueries={analysis.generated_queries || []}
        warning={analysis.warning}
        userShopName={analysis.input_value}
      />
    </div>
  );
}
