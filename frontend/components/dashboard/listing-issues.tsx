"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ListingIssue } from "@/lib/types";

export function ListingIssues({ issues }: { issues: ListingIssue[] }) {
  const grouped = {
    high: issues.filter((i) => i.severity === "high"),
    medium: issues.filter((i) => i.severity === "medium"),
    low: issues.filter((i) => i.severity === "low"),
  };

  const severityVariant = { high: "danger" as const, medium: "warning" as const, low: "outline" as const };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Listing Issues</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {(["high", "medium", "low"] as const).map((severity) => (
          grouped[severity].length > 0 && (
            <div key={severity}>
              <div className="flex items-center gap-2 mb-3">
                <Badge variant={severityVariant[severity]}>{severity.toUpperCase()}</Badge>
                <span className="text-sm text-muted-foreground">{grouped[severity].length} issues</span>
              </div>
              <div className="space-y-3">
                {grouped[severity].map((issue) => (
                  <div key={issue.id} className="rounded-lg border border-border p-4">
                    <p className="font-medium text-sm">{issue.issue}</p>
                    <p className="text-sm text-muted-foreground mt-1">{issue.suggestion}</p>
                    <Badge variant="outline" className="mt-2">{issue.category}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
        {issues.length === 0 && <p className="text-muted-foreground text-sm">No issues detected.</p>}
      </CardContent>
    </Card>
  );
}
