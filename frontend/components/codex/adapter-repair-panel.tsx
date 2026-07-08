"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { runAdapterRepair } from "@/lib/api";
import { PLATFORMS } from "@/lib/types";
import { Loader2 } from "lucide-react";

export function AdapterRepairPanel() {
  const [platform, setPlatform] = useState("etsy");
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runAdapterRepair({
        platform,
        failing_url: url,
        error_message: error,
        adapter_file_path: `backend/app/adapters/${platform}.py`,
      });
      setResult(res.result);
    } catch (e) {
      setResult({ message: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader><CardTitle>Adapter Repair Agent</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
        </Select>
        <Input placeholder="Failing URL" value={url} onChange={(e) => setUrl(e.target.value)} />
        <Input placeholder="Error message" value={error} onChange={(e) => setError(e.target.value)} />
        <Button onClick={handleRun} disabled={loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Run Repair"}</Button>
        {result && (
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
        )}
      </CardContent>
    </Card>
  );
}
