"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import type { AnalysisDetail } from "@/lib/types";
import { BarChart3, DollarSign, Store, AlertTriangle, TrendingUp } from "lucide-react";

export function OverviewCards({ analysis }: { analysis: AnalysisDetail }) {
  const pricing = analysis.pricing_summary;
  const cards = [
    { title: "Listings Analyzed", value: analysis.listings.length, icon: BarChart3 },
    { title: "Average Price", value: formatCurrency(pricing?.average_price || 0), icon: DollarSign },
    { title: "Suggested Range", value: `${formatCurrency(pricing?.suggested_min || 0)} – ${formatCurrency(pricing?.suggested_max || 0)}`, icon: DollarSign },
    { title: "Competitors", value: analysis.competitors.length, icon: Store },
    { title: "Listing Issues", value: analysis.listing_issues.length, icon: AlertTriangle },
    { title: "Trends Found", value: analysis.trends.length, icon: TrendingUp },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
