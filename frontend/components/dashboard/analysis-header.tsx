"use client";

import { Badge, dataSourceBadgeVariant, dataSourceLabel } from "@/components/ui/badge";
import { ShopAnalysisForm } from "@/components/analysis/shop-analysis-form";
import { formatDate } from "@/lib/utils";
import type { AnalysisDetail } from "@/lib/types";
import { Calendar, Globe } from "lucide-react";

export function AnalysisHeader({ analysis }: { analysis: AnalysisDetail }) {
  const isEtsyShop = analysis.platform === "etsy" && analysis.input_type === "shop_name";

  return (
    <div className="dashboard-card p-6 space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-2 min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-primary">Market Analysis</p>
          <h2 className="text-2xl font-bold text-foreground tracking-tight truncate">{analysis.input_value}</h2>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5" />
              {analysis.platform.replace("_", " ")} · {analysis.country}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              {formatDate(analysis.created_at)}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="platform">{analysis.platform.replace("_", " ")}</Badge>
          <Badge variant={analysis.status === "completed" ? "success" : "outline"}>{analysis.status}</Badge>
          <Badge variant={dataSourceBadgeVariant(analysis.data_source)}>
            {dataSourceLabel(analysis.data_source)}
          </Badge>
        </div>
      </div>

      {isEtsyShop && (
        <div className="rounded-xl border border-border bg-muted/20 p-4">
          <p className="text-sm font-medium text-foreground mb-3">Analyze a different Etsy shop</p>
          <ShopAnalysisForm
            compact
            initialShopName=""
            initialCountry={analysis.country}
            initialCurrency={analysis.currency}
          />
        </div>
      )}

      {analysis.warning && <div className="alert-warning">{analysis.warning}</div>}
    </div>
  );
}
