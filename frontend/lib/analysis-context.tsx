"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { getAnalysis } from "@/lib/api";
import type { AnalysisDetail } from "@/lib/types";
import { Shell } from "@/components/layout/shell";
import { AnalysisPageSkeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/error-state";

type AnalysisContextValue = {
  analysis: AnalysisDetail;
  refresh: () => void;
};

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error("useAnalysis must be used within AnalysisLayout");
  return ctx;
}

export function AnalysisLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const id = Number(params.id);
  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!id) return;
    setError(null);
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
    } catch {
      setError("Failed to load analysis. Is the backend running?");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  if (error) {
    return (
      <Shell title="Analysis">
        <ErrorState message={error} onRetry={load} />
      </Shell>
    );
  }

  if (!analysis) {
    return (
      <Shell title="Loading analysis...">
        <AnalysisPageSkeleton />
      </Shell>
    );
  }

  return (
    <AnalysisContext.Provider value={{ analysis, refresh: load }}>
      <Shell
        title={analysis.input_value}
        subtitle={`${analysis.platform.replace("_", " ")} analysis`}
        dataSource={analysis.data_source}
        status={analysis.status}
        platform={analysis.platform.replace("_", " ")}
      >
        <div className="mx-auto max-w-7xl">{children}</div>
      </Shell>
    </AnalysisContext.Provider>
  );
}
