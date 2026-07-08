"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Shell } from "@/components/layout/shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge, dataSourceBadgeVariant, dataSourceLabel } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { createAnalysis, getAnalyses } from "@/lib/api";
import { PLATFORMS, INPUT_TYPES, COUNTRIES, CURRENCIES, type Analysis } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import {
  BarChart3, Search, DollarSign, AlertTriangle, TrendingUp, Sparkles, Package, Wrench, Loader2, ArrowRight,
} from "lucide-react";

const features = [
  { icon: BarChart3, title: "Competitor Intelligence", desc: "Compare shops, reviews, and positioning across marketplaces." },
  { icon: DollarSign, title: "Pricing Analysis", desc: "Find optimal price ranges with under/overpriced detection." },
  { icon: AlertTriangle, title: "Listing Audits", desc: "Detect weak titles, missing tags, and thin descriptions." },
  { icon: TrendingUp, title: "Trend Discovery", desc: "Spot recurring styles, materials, and use cases." },
  { icon: Sparkles, title: "AI Recommendations", desc: "Get grounded title, tag, and pricing suggestions." },
  { icon: Package, title: "Product Expansion", desc: "Discover new product ideas from market gaps." },
  { icon: Wrench, title: "Codex Adapter Repair", desc: "Developer tools for maintaining marketplace extractors." },
];

export default function HomePage() {
  const router = useRouter();
  const [platform, setPlatform] = useState("etsy");
  const [inputType, setInputType] = useState("keyword");
  const [inputValue, setInputValue] = useState("minimalist wall art");
  const [country, setCountry] = useState("US");
  const [currency, setCurrency] = useState("USD");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recent, setRecent] = useState<Analysis[]>([]);
  const [loadingRecent, setLoadingRecent] = useState(true);

  useEffect(() => {
    getAnalyses()
      .then(setRecent)
      .catch(() => {})
      .finally(() => setLoadingRecent(false));
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await createAnalysis({
        platform,
        input_type: inputType as "keyword",
        input_value: inputValue,
        country,
        currency,
      });
      router.push(`/analyses/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell title="Overview" subtitle="AI marketplace intelligence for online sellers">
      <div className="mx-auto max-w-6xl space-y-10">
        <div className="space-y-3">
          <p className="text-sm font-semibold text-primary">ShopPilot</p>
          <h2 className="text-3xl font-bold tracking-tight text-foreground lg:text-4xl">
            AI marketplace intelligence for online sellers.
          </h2>
          <p className="text-base text-muted-foreground max-w-3xl leading-relaxed">
            Analyze listings, competitors, pricing, keywords, and trends across marketplaces.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Search className="h-5 w-5 text-primary" />
              Start new analysis
            </CardTitle>
            <CardDescription>Enter a shop URL, product URL, marketplace URL, or niche keyword.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              <Field label="Platform">
                <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
                  {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                </Select>
              </Field>
              <Field label="Input type">
                <Select value={inputType} onChange={(e) => setInputType(e.target.value)}>
                  {INPUT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </Select>
              </Field>
              <Field label="URL or keyword">
                <Input value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="minimalist wall art" />
              </Field>
              <Field label="Country">
                <Select value={country} onChange={(e) => setCountry(e.target.value)}>
                  {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </Select>
              </Field>
              <Field label="Currency">
                <Select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </Select>
              </Field>
              <div className="flex items-end">
                <Button onClick={handleAnalyze} disabled={loading || !inputValue} className="w-full" size="lg">
                  {loading ? <><Loader2 className="h-4 w-4 animate-spin mr-2" />Analyzing...</> : "Analyze market"}
                </Button>
              </div>
            </div>
            {error && <div className="alert-danger mt-5">{error}</div>}
          </CardContent>
        </Card>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Recent analyses</h3>
          </div>
          {loadingRecent ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-xl" />
              ))}
            </div>
          ) : recent.length > 0 ? (
            <div className="space-y-2">
              {recent.slice(0, 5).map((a) => (
                <button
                  key={a.id}
                  onClick={() => router.push(`/analyses/${a.id}`)}
                  className="w-full flex items-center justify-between rounded-xl border border-border bg-white p-4 hover:shadow-card-hover transition-all text-left group"
                >
                  <div className="min-w-0">
                    <p className="font-medium text-foreground truncate">{a.input_value}</p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      {a.platform.replace("_", " ")} · {formatDate(a.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    <Badge variant={dataSourceBadgeVariant(a.data_source)}>{dataSourceLabel(a.data_source)}</Badge>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-border bg-white px-6 py-10 text-center">
              <p className="text-sm text-muted-foreground">No analyses yet. Run your first market analysis above.</p>
            </div>
          )}
        </div>

        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Platform capabilities</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => {
              const Icon = f.icon;
              return (
                <div key={f.title} className="dashboard-card p-5 hover:shadow-card-hover transition-shadow">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary mb-3">
                    <Icon className="h-4 w-4" />
                  </div>
                  <h4 className="text-sm font-semibold text-foreground">{f.title}</h4>
                  <p className="text-sm text-muted-foreground mt-1.5 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Shell>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="text-sm font-medium text-foreground mb-1.5 block">{label}</label>
      {children}
    </div>
  );
}
