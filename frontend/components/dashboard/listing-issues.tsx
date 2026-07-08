"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import type { ListingIssue } from "@/lib/types";
import { AlertTriangle } from "lucide-react";

export function ListingIssues({ issues }: { issues: ListingIssue[] }) {
  const grouped = {
    high: issues.filter((i) => i.severity === "high"),
    medium: issues.filter((i) => i.severity === "medium"),
    low: issues.filter((i) => i.severity === "low"),
  };

  const severityVariant = { high: "danger" as const, medium: "warning" as const, low: "outline" as const };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-foreground">Listing issues</h3>
        <p className="text-sm text-muted-foreground mt-1">Actionable audit findings grouped by severity.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-primary" />
            Listing audit
          </CardTitle>
        </CardHeader>
        <CardContent>
          {issues.length === 0 ? (
            <EmptyState icon={AlertTriangle} title="No issues detected" description="Your collected listings passed the current audit checks." />
          ) : (
            <div className="space-y-8">
              {(["high", "medium", "low"] as const).map((severity) =>
                grouped[severity].length > 0 ? (
                  <div key={severity}>
                    <div className="flex items-center gap-2 mb-4">
                      <Badge variant={severityVariant[severity]}>{severity.toUpperCase()}</Badge>
                      <span className="text-sm text-muted-foreground">{grouped[severity].length} issues</span>
                    </div>
                    <div className="space-y-3">
                      {grouped[severity].map((issue) => (
                        <div key={issue.id} className="rounded-xl border border-border bg-muted/20 p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline">{issue.category}</Badge>
                          </div>
                          <p className="text-sm font-medium text-foreground">{issue.issue}</p>
                          <p className="text-sm text-muted-foreground mt-2">
                            <span className="font-medium text-foreground">Suggested fix: </span>
                            {issue.suggestion}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
