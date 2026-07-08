"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CodexStatus } from "@/lib/types";
import { Wrench, AlertTriangle } from "lucide-react";

export function CodexStatusCard({ status }: { status: CodexStatus | null }) {
  if (!status) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wrench className="h-5 w-5" />
          Codex Agent Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <Badge variant={status.enabled ? "success" : "warning"}>
            {status.enabled ? "Enabled" : "Disabled"}
          </Badge>
          <span className="text-sm text-muted-foreground">Mode: {status.mode}</span>
        </div>
        <p className="text-sm">{status.message}</p>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">File Patching</p>
            <p className="font-medium">{status.allow_file_patch ? "Allowed" : "Disabled"}</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-muted-foreground">Human Review</p>
            <p className="font-medium">{status.require_human_review ? "Required" : "Optional"}</p>
          </div>
        </div>
        {!status.enabled && (
          <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-4">
            <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5" />
            <div className="text-sm text-amber-800">
              <p className="font-medium">Codex agents are disabled by default.</p>
              <p className="mt-1">Set <code className="bg-amber-100 px-1 rounded">CODEX_AGENTS_ENABLED=true</code> in your .env to enable engineering workflows.</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
