"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PageIntro } from "@/components/layout/page-intro";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getCompetitorDetail } from "@/lib/api";
import { useAnalysis } from "@/lib/analysis-context";
import { formatCurrency } from "@/lib/utils";
import type { CompetitorDetail } from "@/lib/types";
import { ArrowLeft, Store, Tag, TrendingUp } from "lucide-react";

export default function CompetitorDetailPage() {
  const params = useParams<{ id: string; competitorId: string }>();
  const { analysis } = useAnalysis();
  const [detail, setDetail] = useState<CompetitorDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const analysisId = Number(params.id);
    const competitorId = Number(params.competitorId);
    if (!analysisId || !competitorId) return;

    getCompetitorDetail(analysisId, competitorId)
      .then(setDetail)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load competitor detail"));
  }, [params.id, params.competitorId]);

  if (error) {
    return <div className="alert-danger">{error}</div>;
  }

  if (!detail) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href={`/analyses/${analysis.id}/competitors`}
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to discovered competitors
      </Link>

      <PageIntro
        title={detail.competitor_name}
        description={detail.discovered_label || "Similar shop found from marketplace search results."}
      />

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Match score" value={`${detail.match_score.toFixed(0)}/100`} />
        <StatCard label="Listings matched" value={String(detail.product_count)} />
        <StatCard label="Average price" value={formatCurrency(detail.average_price)} />
        <StatCard
          label="Review strength"
          value={`${detail.total_reviews.toLocaleString()}${detail.average_rating > 0 ? ` · ${detail.average_rating.toFixed(1)}★` : ""}`}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Store className="h-4 w-4 text-primary" />
            Why this shop is considered a competitor
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>{detail.positioning_summary}</p>
          {(detail.matched_queries ?? []).length > 0 && (
            <p>
              Matched searches:{" "}
              {(detail.matched_queries ?? []).map((query) => (
                <Badge key={query} variant="outline" className="mr-2 mb-2">
                  {query}
                </Badge>
              ))}
            </p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              Price comparison
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <ComparisonRow label="Your shop avg" value={formatCurrency(detail.price_comparison.user_average_price)} />
            <ComparisonRow label="Competitor avg" value={formatCurrency(detail.price_comparison.competitor_average_price)} />
            <ComparisonRow
              label="Delta"
              value={`${detail.price_comparison.delta >= 0 ? "+" : ""}${formatCurrency(detail.price_comparison.delta)}`}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Tag className="h-4 w-4 text-primary" />
              Keyword overlap
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <KeywordGroup title="Shared keywords" items={detail.keyword_overlap} />
            <KeywordGroup title="Your unique keywords" items={detail.user_unique_keywords} />
            <KeywordGroup title="Competitor unique keywords" items={detail.competitor_unique_keywords} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Competing listings</CardTitle>
        </CardHeader>
        <CardContent>
          {(detail.competing_listings ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No example listings stored for this competitor.</p>
          ) : (
            <div className="space-y-3">
              {(detail.competing_listings ?? []).map((listing) => (
                <div key={`${listing.url}-${listing.title}`} className="flex items-start justify-between gap-4 border-b border-border/80 pb-3">
                  <div>
                    <p className="font-medium text-foreground">{listing.title}</p>
                    {listing.url && (
                      <a href={listing.url} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline">
                        View listing
                      </a>
                    )}
                  </div>
                  <div className="text-right text-sm shrink-0">
                    <p className="font-medium">{formatCurrency(listing.price)}</p>
                    {listing.review_count > 0 && (
                      <p className="text-muted-foreground">{listing.review_count} reviews</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {((detail.product_gaps ?? []).length > 0 || (detail.differentiation_opportunities ?? []).length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Product gaps & differentiation opportunities</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            {(detail.product_gaps ?? []).length > 0 && (
              <KeywordGroup title="Product/theme gaps" items={detail.product_gaps ?? []} />
            )}
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              {(detail.differentiation_opportunities ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-white p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold text-foreground mt-1">{value}</p>
    </div>
  );
}

function ComparisonRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </div>
  );
}

function KeywordGroup({ title, items = [] }: { title: string; items?: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <p className="font-medium text-foreground mb-2">{title}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <Badge key={item} variant="outline">
            {item}
          </Badge>
        ))}
      </div>
    </div>
  );
}
