"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { CodexStatusCard } from "@/components/codex/codex-status-card";
import { AdapterRepairPanel } from "@/components/codex/adapter-repair-panel";
import { ExtractionQAPanel } from "@/components/codex/extraction-qa-panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getCodexStatus, runTestGenerator } from "@/lib/api";
import type { CodexStatus } from "@/lib/types";
import { AlertTriangle, Loader2 } from "lucide-react";

export default function CodexPage() {
  const [status, setStatus] = useState<CodexStatus | null>(null);
  const [targetFile, setTargetFile] = useState("backend/app/adapters/etsy.py");
  const [behavior, setBehavior] = useState("parses Etsy search results");
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCodexStatus().then(setStatus).catch(() => {});
  }, []);

  const handleGenerateTests = async () => {
    setLoading(true);
    try {
      const res = await runTestGenerator({ target_file: targetFile, behavior_description: behavior });
      setTestResult(res.result);
    } catch (e) {
      setTestResult({ message: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell title="Codex Engineering Tools">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Developer Tools</h2>
          <p className="text-muted-foreground mt-1">
            Optional Codex-powered agents for adapter maintenance, extraction QA, and test generation.
          </p>
        </div>

        <CodexStatusCard status={status} />

        <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-4">
          <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5 shrink-0" />
          <div className="text-sm text-red-800">
            <p className="font-medium">Safety Notice</p>
            <p className="mt-1">Codex agents are disabled by default. Patches are never auto-applied unless CODEX_ALLOW_FILE_PATCH=true. Human review is always recommended.</p>
          </div>
        </div>

        <AdapterRepairPanel />
        <ExtractionQAPanel />

        <Card>
          <CardHeader><CardTitle>Test Generator Agent</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Input value={targetFile} onChange={(e) => setTargetFile(e.target.value)} placeholder="Target file" />
            <Input value={behavior} onChange={(e) => setBehavior(e.target.value)} placeholder="Behavior description" />
            <Button onClick={handleGenerateTests} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Generate Tests"}
            </Button>
            {testResult && (
              <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-64">{JSON.stringify(testResult, null, 2)}</pre>
            )}
          </CardContent>
        </Card>
      </div>
    </Shell>
  );
}
