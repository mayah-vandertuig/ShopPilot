import type {
  Analysis,
  AnalysisCreateRequest,
  AnalysisDetail,
  CodexAgentResponse,
  CodexStatus,
  Competitor,
  FreeformResponse,
  Listing,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API error ${res.status}`);
  }
  return res.json();
}

export async function createAnalysis(data: AnalysisCreateRequest): Promise<AnalysisDetail> {
  return fetchApi("/api/analyses", { method: "POST", body: JSON.stringify(data) });
}

export async function getAnalyses(): Promise<Analysis[]> {
  return fetchApi("/api/analyses");
}

export async function getAnalysis(id: number): Promise<AnalysisDetail> {
  return fetchApi(`/api/analyses/${id}`);
}

export async function getListings(analysisId: number): Promise<Listing[]> {
  return fetchApi(`/api/analyses/${analysisId}/listings`);
}

export async function getCompetitors(analysisId: number): Promise<Competitor[]> {
  return fetchApi(`/api/analyses/${analysisId}/competitors`);
}

export async function generateRecommendations(analysisId: number) {
  return fetchApi(`/api/analyses/${analysisId}/recommendations`, { method: "POST" });
}

export async function askFreeformQuestion(analysisId: number, question: string): Promise<FreeformResponse> {
  return fetchApi("/api/search/freeform", {
    method: "POST",
    body: JSON.stringify({ analysis_id: analysisId, question }),
  });
}

export async function getCodexStatus(): Promise<CodexStatus> {
  return fetchApi("/api/codex/status");
}

export async function runAdapterRepair(data: {
  platform: string;
  failing_url: string;
  failing_html_sample?: string;
  error_message?: string;
  adapter_file_path?: string;
}): Promise<CodexAgentResponse> {
  return fetchApi("/api/codex/repair-adapter", { method: "POST", body: JSON.stringify(data) });
}

export async function runExtractionQA(data: {
  platform: string;
  sample_raw_content?: string;
  parsed_listings?: Record<string, unknown>[];
}): Promise<CodexAgentResponse> {
  return fetchApi("/api/codex/extraction-qa", { method: "POST", body: JSON.stringify(data) });
}

export async function runTestGenerator(data: {
  target_file: string;
  behavior_description: string;
}): Promise<CodexAgentResponse> {
  return fetchApi("/api/codex/generate-tests", { method: "POST", body: JSON.stringify(data) });
}
