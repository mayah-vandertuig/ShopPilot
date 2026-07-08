"use client";

import { DollarSign, Store, AlertTriangle, TrendingUp, BarChart3, Target } from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import type { AnalysisDetail } from "@/lib/types";

export function OverviewCards({ analysis }: { analysis: AnalysisDetail }) {
  const pricing = analysis.pricing_summary;
  const cards = [
    { title: "Listings analyzed", value: String(analysis.listings.length), icon: BarChart3 },
    { title: "Average price", value: formatCurrency(pricing?.average_price || 0, analysis.currency), icon: DollarSign },
    {
      title: "Suggested range",
      value: `${formatCurrency(pricing?.suggested_min || 0, analysis.currency)} – ${formatCurrency(pricing?.suggested_max || 0, analysis.currency)}`,
      icon: Target,
    },
    { title: "Competitors found", value: String(analysis.competitors.length), icon: Store },
    { title: "Issues found", value: String(analysis.listing_issues.length), icon: AlertTriangle },
    { title: "Trends found", value: String(analysis.trends.length), icon: TrendingUp },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.title} className="dashboard-card p-5 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-medium text-muted-foreground">{card.title}</p>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <p className="text-xl font-bold text-foreground leading-tight">{card.value}</p>
          </div>
        );
      })}
    </div>
  );
}
