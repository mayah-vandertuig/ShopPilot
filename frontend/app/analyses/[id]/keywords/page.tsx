"use client";

import { KeywordCloud } from "@/components/dashboard/keyword-cloud";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function KeywordsPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="Keywords" description="High-frequency terms, shared tags, and gaps in your niche coverage." />
      <KeywordCloud analysis={analysis} />
    </div>
  );
}
