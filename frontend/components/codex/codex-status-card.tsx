"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CodexStatus } from "@/lib/types";
import { Wrench, AlertTriangle, CheckCircle2 } from "lucide-react";

export function CodexStatusCard({ status }: { status: CodexStatus | null }) {
  if (!status) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wrench className="h-5 w-5 text-primary" />
          Codex agent status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex items-center gap-3">
          {status.enabled ? (
            <Badge variant="success" className="gap-1"><CheckCircle2 className="h-3 w-3" /> Enabled</Badge>
          ) : (
            <Badge variant="warning">Disabled</Badge>
          )}
          <span className="text-sm text-muted-foreground">Mode: {status.mode}</span>
        </div>
        <p className="text-sm text-foreground">{status.message}</p>
        <div className="grid grid-cols-2 gap-4">
          <Stat label="File patching" value={status.allow_file_patch ? "Allowed" : "Disabled"} />
          <Stat label="Human review" value={status.require_human_review ? "Required" : "Optional"} />
        </div>
        {!status.enabled && (
          <div className="alert-warning flex items-start gap-3">
            <AlertTriangle className="h-4 w-4 text-warning shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Codex is disabled</p>
              <p className="mt-1">
                Set <code className="rounded bg-amber-100 px-1.5 py-0.5 text-xs">CODEX_AGENTS_ENABLED=true</code> in your <code className="rounded bg-amber-100 px-1.5 py-0.5 text-xs">.env</code> and restart the backend.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-semibold text-foreground mt-1">{value}</p>
    </div>
  );
}
