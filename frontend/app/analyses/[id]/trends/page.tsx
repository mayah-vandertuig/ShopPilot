"use client";

import { TrendsPanel } from "@/components/dashboard/trends-panel";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function TrendsPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="Trends" description="Recurring patterns surfaced from titles, tags, and descriptions." />
      <TrendsPanel trends={analysis.trends} />
    </div>
  );
}
