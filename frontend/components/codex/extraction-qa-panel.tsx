"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { runExtractionQA } from "@/lib/api";
import { PLATFORMS } from "@/lib/types";
import { Loader2, ScanSearch } from "lucide-react";

export function ExtractionQAPanel() {
  const [platform, setPlatform] = useState("etsy");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runExtractionQA({ platform, parsed_listings: [] });
      setResult(res.result);
    } catch {
      setResult({ message: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ScanSearch className="h-4 w-4 text-primary" />
          Extraction QA Agent
        </CardTitle>
        <CardDescription>Score extraction quality and find missing fields.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
        </Select>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Run QA"}
        </Button>
        {result && <pre className="text-xs bg-muted/50 border border-border p-3 rounded-xl overflow-auto max-h-48">{JSON.stringify(result, null, 2)}</pre>}
      </CardContent>
    </Card>
  );
}
