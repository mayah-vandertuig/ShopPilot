"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { CodexStatusCard } from "@/components/codex/codex-status-card";
import { AdapterRepairPanel } from "@/components/codex/adapter-repair-panel";
import { ExtractionQAPanel } from "@/components/codex/extraction-qa-panel";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getCodexStatus, runTestGenerator } from "@/lib/api";
import type { CodexStatus } from "@/lib/types";
import { AlertTriangle, Loader2, Shield, Wrench } from "lucide-react";

export default function CodexPage() {
  const [status, setStatus] = useState<CodexStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [targetFile, setTargetFile] = useState("backend/app/adapters/etsy.py");
  const [behavior, setBehavior] = useState("parses Etsy search results");
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCodexStatus()
      .then(setStatus)
      .catch(() => {})
      .finally(() => setLoadingStatus(false));
  }, []);

  const handleGenerateTests = async () => {
    setLoading(true);
    try {
      const res = await runTestGenerator({ target_file: targetFile, behavior_description: behavior });
      setTestResult(res.result);
    } catch {
      setTestResult({ message: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell title="Codex Tools" subtitle="Engineering agents for adapter maintenance and extraction QA">
      <div className="mx-auto max-w-5xl space-y-8">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Wrench className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold text-foreground">Developer tooling</h2>
          </div>
          <p className="text-muted-foreground max-w-2xl">
            Optional Codex-powered agents for adapter repair, extraction QA, and test generation. Not part of the seller workflow.
          </p>
        </div>

        {loadingStatus ? <Skeleton className="h-40 w-full rounded-xl" /> : <CodexStatusCard status={status} />}

        <div className="alert-danger">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-danger shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Safety settings</p>
              <p className="mt-1">
                Codex agents are disabled by default. Patches are never auto-applied unless{" "}
                <code className="rounded bg-red-100 px-1.5 py-0.5 text-xs">CODEX_ALLOW_FILE_PATCH=true</code>.
                Human review is always recommended.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <AdapterRepairPanel />
          <ExtractionQAPanel />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Test Generator Agent</CardTitle>
            <CardDescription>Generate pytest coverage for adapter and analysis behavior.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input value={targetFile} onChange={(e) => setTargetFile(e.target.value)} placeholder="Target file" />
            <Input value={behavior} onChange={(e) => setBehavior(e.target.value)} placeholder="Behavior description" />
            <Button onClick={handleGenerateTests} disabled={loading || !status?.enabled}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Generate tests"}
            </Button>
            {!status?.enabled && (
              <p className="text-sm text-muted-foreground">Enable Codex in your environment to run this agent.</p>
            )}
            {testResult && (
              <pre className="text-xs bg-muted/50 border border-border p-4 rounded-xl overflow-auto max-h-64">{JSON.stringify(testResult, null, 2)}</pre>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              Human review requirement
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge variant={status?.require_human_review ? "success" : "warning"}>
              Human review: {status?.require_human_review ? "Required" : "Optional"}
            </Badge>
            <Badge variant={status?.allow_file_patch ? "warning" : "success"}>
              File patching: {status?.allow_file_patch ? "Allowed" : "Disabled"}
            </Badge>
            <Badge variant="outline">Mode: {status?.mode || "subprocess"}</Badge>
          </CardContent>
        </Card>
      </div>
    </Shell>
  );
}
