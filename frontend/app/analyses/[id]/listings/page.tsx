"use client";

import { ListingTable } from "@/components/listings/listing-table";
import { PageIntro } from "@/components/layout/page-intro";
import { useAnalysis } from "@/lib/analysis-context";

export default function ListingsPage() {
  const { analysis } = useAnalysis();
  return (
    <div className="space-y-6">
      <PageIntro title="Listings" description="Browse collected products, filter by shop or title, and inspect details." />
      <ListingTable listings={analysis.listings} issues={analysis.listing_issues} />
    </div>
  );
}
