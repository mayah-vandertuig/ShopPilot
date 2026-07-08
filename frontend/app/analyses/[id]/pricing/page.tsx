"use client";

import { PricingChart } from "@/components/dashboard/pricing-chart";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function PricingPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="Pricing" description="Distribution, benchmarks, and pricing opportunities across collected listings." />
      <PricingChart analysis={analysis} />
    </div>
  );
}
