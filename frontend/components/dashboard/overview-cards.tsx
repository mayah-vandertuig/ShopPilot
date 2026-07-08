"use client";

import Link from "next/link";
import {
  Store, AlertTriangle, BarChart3, Hash, Lightbulb, ArrowRight,
} from "lucide-react";
import { Badge, dataSourceBadgeVariant, dataSourceLabel } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import {
  getDetectedNiche,
  getMainOpportunity,
  getRecommendedActions,
  getStrongestCompetitor,
  getTopProductThemes,
  getUserListings,
} from "@/lib/analysis-insights";
import type { AnalysisDetail } from "@/lib/types";

export function OverviewCards({ analysis }: { analysis: AnalysisDetail }) {
  const userListings = getUserListings(analysis);
  const topKeyword =
    analysis.keyword_summary?.summary_stats?.top_opportunity_tag ||
    analysis.keyword_summary?.top_keywords?.[0]?.keyword ||
    "—";
  const strongest = getStrongestCompetitor(analysis);
  const themes = getTopProductThemes(analysis);
  const hasData = userListings.length > 0;

  if (!hasData) {
    return (
      <EmptyState
        icon={BarChart3}
        title="No analysis data yet"
        description="Run an Etsy shop analysis to see competitors, keywords, and listing insights for your catalog."
        action={
          <Link href="/">
            <Button>Analyze an Etsy shop</Button>
          </Link>
        }
      />
    );
  }

  const statCards = [
    { title: "Listings analyzed", value: String(userListings.length), icon: BarChart3 },
    { title: "Competitors discovered", value: String((analysis.competitors ?? []).length), icon: Store },
    { title: "Top tag opportunity", value: topKeyword, icon: Hash },
    { title: "Issues found", value: String(analysis.listing_issues.length), icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      <div className="dashboard-card p-6 space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-primary">Shop summary</p>
            <h3 className="text-xl font-bold text-foreground mt-1">{analysis.input_value}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Etsy · {analysis.country} · analyzed {formatDate(analysis.created_at)}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="platform">Etsy</Badge>
            <Badge variant={analysis.status === "completed" ? "success" : "outline"}>{analysis.status}</Badge>
            <Badge variant={dataSourceBadgeVariant(analysis.data_source)}>
              {dataSourceLabel(analysis.data_source)}
            </Badge>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 text-sm">
          <Insight label="Detected niche" value={getDetectedNiche(analysis)} />
          <Insight label="Top product themes" value={themes.join(", ") || "—"} />
          <Insight label="Strongest competitor" value={strongest?.competitor_name || "—"} />
          <Insight label="Main opportunity" value={getMainOpportunity(analysis)} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.title} className="dashboard-card p-5 hover:shadow-card-hover transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-medium text-muted-foreground">{card.title}</p>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <p className="text-lg font-bold text-foreground leading-tight">{card.value}</p>
            </div>
          );
        })}
      </div>

      {getRecommendedActions(analysis).length > 0 && (
        <div className="dashboard-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-foreground">Recommended next actions</h3>
          </div>
          <ul className="space-y-2">
            {getRecommendedActions(analysis).map((action) => (
              <li key={action} className="flex items-start gap-2 text-sm text-muted-foreground">
                <ArrowRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Insight({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-muted/20 p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium text-foreground mt-1 leading-snug">{value}</p>
    </div>
  );
}
