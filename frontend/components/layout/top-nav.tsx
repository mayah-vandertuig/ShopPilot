"use client";

import { Badge } from "@/components/ui/badge";

export function TopNav({ title, dataSource }: { title?: string; dataSource?: string }) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-white px-6">
      <div>
        <h1 className="text-lg font-semibold">{title || "ShopPilot"}</h1>
        <p className="text-sm text-muted-foreground">Marketplace intelligence dashboard</p>
      </div>
      <div className="flex items-center gap-3">
        {dataSource && (
          <Badge variant={dataSource === "live" ? "success" : "warning"}>
            {dataSource === "live" ? "Live Data" : "Mock Data"}
          </Badge>
        )}
      </div>
    </header>
  );
}
