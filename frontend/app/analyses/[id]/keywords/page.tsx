"use client";

import { KeywordIntelligence } from "@/components/dashboard/keyword-intelligence";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function KeywordsPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro
        title="Keyword & Tag Intelligence"
        description="Research tag opportunities, competitor usage, and long-tail phrases to improve your Etsy listings."
      />
      <KeywordIntelligence analysis={analysis} />
    </div>
  );
}
