"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { askFreeformQuestion } from "@/lib/api";
import { MessageSquare, Loader2 } from "lucide-react";

export function FreeformSearch({ analysisId }: { analysisId: number }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<string[]>([]);
  const [uncertainty, setUncertainty] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await askFreeformQuestion(analysisId, question);
      setAnswer(result.answer);
      setEvidence(result.supporting_evidence);
      setUncertainty(result.uncertainty_notes);
    } catch (e) {
      setAnswer(null);
      setError(e instanceof Error ? e.message : "Failed to get answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-primary" />
          Ask about this market
        </CardTitle>
        <p className="text-sm text-muted-foreground">Free-form questions grounded in your analysis data.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="e.g. What price should I target for canvas prints?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          />
          <Button onClick={handleAsk} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Ask"}
          </Button>
        </div>
        {error && <div className="alert-danger">{error}</div>}
        {answer && (
          <div className="rounded-xl border border-border bg-muted/30 p-5 space-y-4">
            <p className="text-sm text-foreground leading-relaxed">{answer}</p>
            {evidence.length > 0 && (
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Supporting evidence</p>
                <ul className="text-sm space-y-1.5 text-foreground">{evidence.map((e, i) => <li key={i}>• {e}</li>)}</ul>
              </div>
            )}
            {uncertainty.length > 0 && (
              <div className="alert-warning">
                <p className="text-xs font-semibold uppercase tracking-wide mb-2">Uncertainty notes</p>
                <ul className="space-y-1">{uncertainty.map((u, i) => <li key={i}>• {u}</li>)}</ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
