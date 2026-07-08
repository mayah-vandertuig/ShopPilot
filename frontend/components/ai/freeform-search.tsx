"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { askFreeformQuestion } from "@/lib/api";
import { MessageSquare, Loader2 } from "lucide-react";

export function FreeformSearch({ analysisId }: { analysisId: number }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<string[]>([]);
  const [uncertainty, setUncertainty] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<string | null>(null);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const result = await askFreeformQuestion(analysisId, question);
      setAnswer(result.answer);
      setEvidence(result.supporting_evidence);
      setUncertainty(result.uncertainty_notes);
      setDataSource(result.data_source);
    } catch (e) {
      setAnswer("Failed to get answer. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary" />
          Ask About This Market
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="e.g. What price should I target for minimalist canvas prints?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          />
          <Button onClick={handleAsk} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Ask"}
          </Button>
        </div>
        {answer && (
          <div className="rounded-lg bg-muted p-4 space-y-3">
            {dataSource && <Badge variant={dataSource === "live" ? "success" : "warning"}>{dataSource} response</Badge>}
            <p className="text-sm">{answer}</p>
            {evidence.length > 0 && (
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">Supporting Evidence</p>
                <ul className="text-sm space-y-1">{evidence.map((e, i) => <li key={i}>• {e}</li>)}</ul>
              </div>
            )}
            {uncertainty.length > 0 && (
              <div>
                <p className="text-xs font-medium text-amber-600 mb-1">Uncertainty Notes</p>
                <ul className="text-sm text-amber-700 space-y-1">{uncertainty.map((u, i) => <li key={i}>• {u}</li>)}</ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
