"use client";

import { CompetitorTable } from "@/components/dashboard/competitor-table";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function CompetitorsPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="Competitors" description="Shops ranked by catalog depth, pricing, and review volume." />
      <CompetitorTable competitors={analysis.competitors} />
    </div>
  );
}
