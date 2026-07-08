"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Shell } from "@/components/layout/shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { createAnalysis, getAnalyses } from "@/lib/api";
import { PLATFORMS, INPUT_TYPES, COUNTRIES, CURRENCIES, type Analysis } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import {
  BarChart3, Search, DollarSign, AlertTriangle, TrendingUp, Sparkles, Package, Wrench, Loader2,
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

  useEffect(() => {
    getAnalyses().then(setRecent).catch(() => {});
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
    <Shell title="ShopPilot">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-3 py-6">
          <h2 className="text-3xl font-bold tracking-tight">
            AI-Powered Marketplace Intelligence
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Analyze competitors, optimize pricing, audit listings, discover trends, and get AI recommendations across Etsy, Google Shopping, and more.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              Start New Analysis
            </CardTitle>
            <CardDescription>Enter a shop URL, product URL, marketplace URL, or niche keyword.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Platform</label>
                <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
                  {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Input Type</label>
                <Select value={inputType} onChange={(e) => setInputType(e.target.value)}>
                  {INPUT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Input Value</label>
                <Input value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="minimalist wall art" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Country</label>
                <Select value={country} onChange={(e) => setCountry(e.target.value)}>
                  {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Currency</label>
                <Select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </Select>
              </div>
              <div className="flex items-end">
                <Button onClick={handleAnalyze} disabled={loading || !inputValue} className="w-full" size="lg">
                  {loading ? <><Loader2 className="h-4 w-4 animate-spin mr-2" />Analyzing...</> : "Analyze Market"}
                </Button>
              </div>
            </div>
            {error && <p className="text-sm text-red-600 mt-4">{error}</p>}
          </CardContent>
        </Card>

        {recent.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Recent Analyses</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recent.slice(0, 5).map((a) => (
                  <button
                    key={a.id}
                    onClick={() => router.push(`/analyses/${a.id}`)}
                    className="w-full flex items-center justify-between rounded-lg border border-border p-4 hover:bg-muted/50 transition-colors text-left"
                  >
                    <div>
                      <p className="font-medium">{a.input_value}</p>
                      <p className="text-sm text-muted-foreground">{a.platform} · {formatDate(a.created_at)}</p>
                    </div>
                    <Badge variant={a.data_source === "live" ? "success" : "warning"}>{a.data_source}</Badge>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <Card key={f.title}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Icon className="h-4 w-4 text-primary" />
                    {f.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{f.desc}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </Shell>
  );
}
