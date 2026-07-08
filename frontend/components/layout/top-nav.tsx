"use client";

import { Badge, dataSourceBadgeVariant, dataSourceLabel } from "@/components/ui/badge";

export function TopNav({
  title,
  subtitle,
  dataSource,
  status,
  platform,
}: {
  title?: string;
  subtitle?: string;
  dataSource?: string;
  status?: string;
  platform?: string;
}) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-white/90 backdrop-blur px-6">
      <div className="min-w-0">
        <h1 className="text-base font-semibold text-foreground truncate">{title || "ShopPilot"}</h1>
        {subtitle && <p className="text-sm text-muted-foreground truncate">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {platform && <Badge variant="platform">{platform}</Badge>}
        {status && <Badge variant="outline">{status}</Badge>}
        {dataSource && (
          <Badge variant={dataSourceBadgeVariant(dataSource)}>{dataSourceLabel(dataSource)}</Badge>
        )}
      </div>
    </header>
  );
}
