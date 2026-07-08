"use client";

import { AnalysisHeader } from "@/components/dashboard/analysis-header";
import { OverviewCards } from "@/components/dashboard/overview-cards";
import { ListingIssues } from "@/components/dashboard/listing-issues";
import { useAnalysis } from "@/lib/analysis-context";

export default function AnalysisOverviewPage() {
  const { analysis } = useAnalysis();

  return (
    <div className="space-y-8">
      <AnalysisHeader analysis={analysis} />
      <OverviewCards analysis={analysis} />
      <ListingIssues issues={analysis.listing_issues} />
    </div>
  );
}
