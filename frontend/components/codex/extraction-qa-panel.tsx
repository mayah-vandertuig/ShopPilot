"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { runExtractionQA } from "@/lib/api";
import { PLATFORMS } from "@/lib/types";
import { Loader2 } from "lucide-react";

export function ExtractionQAPanel() {
  const [platform, setPlatform] = useState("etsy");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runExtractionQA({ platform, parsed_listings: [] });
      setResult(res.result);
    } catch (e) {
      setResult({ message: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader><CardTitle>Extraction QA Agent</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
        </Select>
        <Button onClick={handleRun} disabled={loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Run QA"}</Button>
        {result && (
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
        )}
      </CardContent>
    </Card>
  );
}
