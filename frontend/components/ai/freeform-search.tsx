"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { askFreeformQuestion } from "@/lib/api";
import { MessageSquare, Loader2 } from "lucide-react";

const SAMPLE_QUESTIONS = [
  "What price range should I target?",
  "Which tags am I missing compared to competitors?",
  "How should I position my shop against competitors?",
  "What product ideas fit this niche?",
];

export function FreeformSearch({
  analysisId,
  disabled = false,
}: {
  analysisId: number;
  disabled?: boolean;
}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<string[]>([]);
  const [uncertainty, setUncertainty] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (value?: string) => {
    const q = (value ?? question).trim();
    if (!q || disabled) return;
    setQuestion(q);
    setLoading(true);
    setError(null);
    try {
      const result = await askFreeformQuestion(analysisId, q);
      setAnswer(result.answer);
      setEvidence(Array.isArray(result.supporting_evidence) ? result.supporting_evidence.map(String) : []);
      setUncertainty(Array.isArray(result.uncertainty_notes) ? result.uncertainty_notes.map(String) : []);
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
            disabled={disabled || loading}
          />
          <Button onClick={() => handleAsk()} disabled={loading || disabled || !question.trim()}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Ask"}
          </Button>
        </div>
        {!disabled && (
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUESTIONS.map((sample) => (
              <button
                key={sample}
                type="button"
                onClick={() => handleAsk(sample)}
                disabled={loading}
                className="rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground transition-colors disabled:opacity-50"
              >
                {sample}
              </button>
            ))}
          </div>
        )}
        {error && <div className="alert-danger">{error}</div>}
        {disabled && (
          <p className="text-sm text-muted-foreground text-center py-4">
            Scrape listing data first to ask questions about this market.
          </p>
        )}
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
