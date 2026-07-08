"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import type { AnalysisDetail, KeywordInsight } from "@/lib/types";
import {
  Hash,
  TrendingUp,
  TrendingDown,
  Minus,
  Search,
  Lightbulb,
  Target,
  AlertTriangle,
  Sparkles,
  X,
  ArrowUpDown,
} from "lucide-react";

type FilterKey =
  | "all"
  | "missing"
  | "long-tail"
  | "high-opportunity"
  | "high-competition"
  | "competitor-used"
  | "my-shop"
  | "style"
  | "product"
  | "room"
  | "theme"
  | "format";

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All tags" },
  { key: "missing", label: "Missing opportunities" },
  { key: "long-tail", label: "Long-tail tags" },
  { key: "high-opportunity", label: "High opportunity" },
  { key: "high-competition", label: "High competition" },
  { key: "competitor-used", label: "Used by competitors" },
  { key: "my-shop", label: "Used by my shop" },
  { key: "style", label: "Style" },
  { key: "product", label: "Product" },
  { key: "room", label: "Room" },
  { key: "theme", label: "Theme" },
  { key: "format", label: "Format" },
];

type SortKey = "opportunity_score" | "competitor_usage_count" | "user_usage_count" | "tag";

export function KeywordIntelligence({ analysis }: { analysis: AnalysisDetail }) {
  const summary = analysis.keyword_summary;
  const insights = summary?.tag_insights || [];
  const stats = summary?.summary_stats;
  const missing = summary?.missing_tag_opportunities || [];
  const longTail = summary?.long_tail_opportunities || [];
  const gap = summary?.tag_gap_analysis;
  const clusters = summary?.keyword_clusters || [];
  const actions = summary?.suggested_actions || [];

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterKey>("all");
  const [sortKey, setSortKey] = useState<SortKey>("opportunity_score");
  const [sortAsc, setSortAsc] = useState(false);
  const [selectedTag, setSelectedTag] = useState<KeywordInsight | null>(null);

  const filteredInsights = useMemo(() => {
    let items = [...insights];
    const q = search.trim().toLowerCase();
    if (q) items = items.filter((i) => i.tag.includes(q));

    switch (filter) {
      case "missing":
        items = items.filter((i) => i.competitor_usage_count >= 2 && i.user_usage_count < 2);
        break;
      case "long-tail":
        items = items.filter((i) => i.tag.split(" ").length >= 2);
        break;
      case "high-opportunity":
        items = items.filter((i) => i.opportunity_score >= 70);
        break;
      case "high-competition":
        items = items.filter((i) => i.competition_estimate === "High");
        break;
      case "competitor-used":
        items = items.filter((i) => i.competitor_usage_count > 0);
        break;
      case "my-shop":
        items = items.filter((i) => i.user_usage_count > 0);
        break;
      case "style":
      case "product":
      case "room":
      case "theme":
      case "format":
        items = items.filter((i) => i.keyword_type === filter);
        break;
    }

    items.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string" && typeof bv === "string") {
        return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
      }
      return sortAsc ? Number(av) - Number(bv) : Number(bv) - Number(av);
    });
    return items;
  }, [insights, search, filter, sortKey, sortAsc]);

  if (!insights.length && !summary?.top_keywords?.length) {
    return (
      <EmptyState
        icon={Hash}
        title="No tag data yet"
        description="Tag intelligence appears once listing titles and tags are analyzed."
      />
    );
  }

  const hasIntelligence = insights.length > 0;

  return (
    <div className="space-y-6">
      {hasIntelligence && stats && (
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          <SummaryCard label="Tags analyzed" value={String(stats.total_tags_analyzed)} />
          <SummaryCard label="Top opportunity" value={stats.top_opportunity_tag || "—"} small />
          <SummaryCard label="Top competitor tag" value={stats.highest_competitor_tag || "—"} small />
          <SummaryCard label="Missing tags" value={String(stats.missing_tags_count)} />
          <SummaryCard label="Overused/generic" value={String(stats.overused_generic_count)} />
          <SummaryCard label="Long-tail opportunities" value={String(stats.long_tail_count)} />
        </div>
      )}

      {hasIntelligence && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Top Tags
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Ranked tag opportunities based on competitor usage, estimated demand, and gap analysis.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div className="relative max-w-sm w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search tags..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full rounded-lg border border-border bg-white pl-9 pr-3 py-2 text-sm"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {FILTERS.map((f) => (
                  <button
                    key={f.key}
                    onClick={() => setFilter(f.key)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                      filter === f.key
                        ? "bg-primary text-white"
                        : "border border-border bg-white text-muted-foreground hover:bg-muted/50"
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/30 text-left">
                    <SortHeader label="Tag" sortKey="tag" current={sortKey} asc={sortAsc} onSort={handleSort} />
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Type</th>
                    <SortHeader label="Competitors" sortKey="competitor_usage_count" current={sortKey} asc={sortAsc} onSort={handleSort} />
                    <SortHeader label="My shop" sortKey="user_usage_count" current={sortKey} asc={sortAsc} onSort={handleSort} />
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Est. demand</th>
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Competition</th>
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Engagement</th>
                    <SortHeader label="Score" sortKey="opportunity_score" current={sortKey} asc={sortAsc} onSort={handleSort} />
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Trend</th>
                    <th className="px-3 py-2.5 font-medium text-muted-foreground">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInsights.slice(0, 25).map((insight) => (
                    <tr
                      key={insight.tag}
                      className="border-b border-border last:border-0 hover:bg-muted/20 cursor-pointer"
                      onClick={() => setSelectedTag(insight)}
                    >
                      <td className="px-3 py-2.5 font-medium">
                        <div className="flex items-center gap-2 flex-wrap">
                          {insight.tag}
                          {insight.competitor_usage_count >= 2 && insight.user_usage_count < 2 && (
                            <Badge variant="warning" className="text-[10px]">Missing</Badge>
                          )}
                          {insight.competitor_usage_count >= 3 && (
                            <Badge variant="outline" className="text-[10px]">Competitor-used</Badge>
                          )}
                        </div>
                      </td>
                      <td className="px-3 py-2.5">
                        <TypeBadge type={insight.keyword_type} />
                      </td>
                      <td className="px-3 py-2.5">{insight.competitor_usage_count}</td>
                      <td className="px-3 py-2.5">{insight.user_usage_count}</td>
                      <td className="px-3 py-2.5">
                        <EstimateBadge value={insight.search_volume_estimate} />
                      </td>
                      <td className="px-3 py-2.5">
                        <EstimateBadge value={insight.competition_estimate} />
                      </td>
                      <td className="px-3 py-2.5 capitalize">{insight.engagement_estimate}</td>
                      <td className="px-3 py-2.5">
                        <ScoreBadge score={insight.opportunity_score} />
                      </td>
                      <td className="px-3 py-2.5">
                        <TrendIndicator direction={insight.trend_direction} />
                      </td>
                      <td className="px-3 py-2.5 text-xs text-muted-foreground max-w-[200px] truncate">
                        {insight.suggested_action}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {filteredInsights.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">No tags match your filters.</p>
            )}
          </CardContent>
        </Card>
      )}

      {missing.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-warning" />
              Missing tag opportunities
            </CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="pb-2 font-medium text-muted-foreground">Tag</th>
                  <th className="pb-2 font-medium text-muted-foreground">Competitors</th>
                  <th className="pb-2 font-medium text-muted-foreground">My usage</th>
                  <th className="pb-2 font-medium text-muted-foreground">Example listings</th>
                  <th className="pb-2 font-medium text-muted-foreground">Why it matters</th>
                  <th className="pb-2 font-medium text-muted-foreground">Add to</th>
                </tr>
              </thead>
              <tbody>
                {missing.slice(0, 8).map((item) => (
                  <tr key={item.tag} className="border-b border-border last:border-0">
                    <td className="py-2.5 font-medium">{item.tag}</td>
                    <td className="py-2.5">{item.competitor_usage_count}</td>
                    <td className="py-2.5">{item.user_usage_count}</td>
                    <td className="py-2.5 text-xs text-muted-foreground max-w-[180px]">
                      {item.example_competitor_listings?.[0]?.title || "—"}
                    </td>
                    <td className="py-2.5 text-xs text-muted-foreground max-w-[200px]">{item.why_it_matters}</td>
                    <td className="py-2.5 text-xs">{item.suggested_listings_to_add?.[0] || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {longTail.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              Long-tail tag opportunities
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Specific multi-word phrases that may be easier to rank for on Etsy.
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {longTail.map((item) => (
                <div key={item.tag} className="rounded-xl border border-border bg-muted/20 p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium text-foreground">{item.tag}</p>
                    <ScoreBadge score={item.opportunity_score} />
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs">
                    <Badge variant="outline">Demand: {item.estimated_demand}</Badge>
                    <Badge variant="outline">Competition: {item.estimated_competition}</Badge>
                    <Badge variant="outline">{item.recommended_listing_type}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Title: <span className="text-foreground">{item.suggested_title_phrase}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Etsy tag: <span className="text-foreground">{item.suggested_etsy_tag}</span>
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {gap && (
        <Card>
          <CardHeader>
            <CardTitle>Tag gap analysis</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <GapGroup title="Tags I use often" items={gap.user_frequent_tags ?? []} tone="primary" />
            <GapGroup title="Tags competitors use often" items={gap.competitor_frequent_tags ?? []} />
            <GapGroup title="Tags both use" items={gap.shared_tags ?? []} tone="success" />
            <GapGroup title="Missing from my shop" items={gap.missing_tags ?? []} tone="warning" />
            <GapGroup title="Weak/generic tags I use" items={gap.weak_generic_tags ?? []} tone="danger" />
          </CardContent>
        </Card>
      )}

      {clusters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Keyword clusters</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {clusters.map((cluster) => (
              <div key={cluster.name} className="rounded-xl border border-border bg-muted/20 p-4">
                <p className="text-sm font-semibold text-foreground">{cluster.name}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {cluster.keywords.map((keyword) => (
                    <span key={keyword} className="rounded-full border border-border bg-white px-2.5 py-1 text-xs text-muted-foreground">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {actions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              Suggested actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {actions.map((action) => (
                <li key={action}>• {action}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {!hasIntelligence && summary && (
        <LegacyKeywordFallback summary={summary} />
      )}

      {selectedTag && (
        <TagDetailDrawer insight={selectedTag} onClose={() => setSelectedTag(null)} />
      )}
    </div>
  );

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  }
}

function SummaryCard({ label, value, small }: { label: string; value: string; small?: boolean }) {
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`font-semibold text-foreground mt-1 ${small ? "text-sm truncate" : "text-xl"}`}>{value}</p>
    </div>
  );
}

function SortHeader({
  label,
  sortKey,
  current,
  asc,
  onSort,
}: {
  label: string;
  sortKey: SortKey;
  current: SortKey;
  asc: boolean;
  onSort: (key: SortKey) => void;
}) {
  return (
    <th className="px-3 py-2.5 font-medium text-muted-foreground">
      <button
        className="flex items-center gap-1 hover:text-foreground"
        onClick={() => onSort(sortKey)}
      >
        {label}
        <ArrowUpDown className={`h-3 w-3 ${current === sortKey ? "text-primary" : ""}`} />
        {current === sortKey && <span className="text-[10px]">{asc ? "↑" : "↓"}</span>}
      </button>
    </th>
  );
}

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    style: "bg-violet-50 text-violet-700 border-violet-200",
    product: "bg-blue-50 text-blue-700 border-blue-200",
    room: "bg-emerald-50 text-emerald-700 border-emerald-200",
    theme: "bg-amber-50 text-amber-700 border-amber-200",
    format: "bg-sky-50 text-sky-700 border-sky-200",
    seasonal: "bg-pink-50 text-pink-700 border-pink-200",
    audience: "bg-orange-50 text-orange-700 border-orange-200",
  };
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[10px] font-medium capitalize ${colors[type] || "border-border text-muted-foreground"}`}>
      {type}
    </span>
  );
}

function EstimateBadge({ value }: { value: string }) {
  const variant = value === "High" ? "danger" : value === "Medium" ? "warning" : "success";
  return <Badge variant={variant as "danger" | "warning" | "success"}>{value}</Badge>;
}

function ScoreBadge({ score }: { score: number }) {
  const variant = score >= 75 ? "success" : score >= 50 ? "warning" : "outline";
  return <Badge variant={variant}>{score}</Badge>;
}

function TrendIndicator({ direction }: { direction: string }) {
  if (direction === "rising") {
    return <span className="flex items-center gap-1 text-emerald-600 text-xs"><TrendingUp className="h-3 w-3" /> Rising</span>;
  }
  if (direction === "declining") {
    return <span className="flex items-center gap-1 text-red-600 text-xs"><TrendingDown className="h-3 w-3" /> Declining</span>;
  }
  return <span className="flex items-center gap-1 text-muted-foreground text-xs"><Minus className="h-3 w-3" /> Stable</span>;
}

function GapGroup({
  title,
  items = [],
  tone = "default",
}: {
  title: string;
  items?: string[];
  tone?: "default" | "primary" | "success" | "warning" | "danger";
}) {
  const toneClass = {
    default: "border-border bg-muted/20",
    primary: "border-primary/20 bg-primary/5",
    success: "border-emerald-200 bg-emerald-50",
    warning: "border-amber-200 bg-amber-50",
    danger: "border-red-200 bg-red-50",
  }[tone];

  return (
    <div className={`rounded-xl border p-4 ${toneClass}`}>
      <p className="text-sm font-semibold text-foreground mb-2">{title}</p>
      {items.length === 0 ? (
        <p className="text-xs text-muted-foreground">None detected</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {items.map((item) => (
            <span key={item} className="rounded-full border border-border bg-white px-2 py-0.5 text-xs">
              {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function TagDetailDrawer({ insight, onClose }: { insight: KeywordInsight; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white shadow-xl overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-border p-4 flex items-center justify-between">
          <h3 className="font-semibold text-foreground">Tag detail</h3>
          <button onClick={onClose} className="rounded-lg p-1 hover:bg-muted">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <p className="text-lg font-semibold">{insight.tag}</p>
            <div className="flex items-center gap-2 mt-2">
              <TypeBadge type={insight.keyword_type} />
              <ScoreBadge score={insight.opportunity_score} />
              <TrendIndicator direction={insight.trend_direction} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg border border-border p-3">
              <p className="text-xs text-muted-foreground">Competitor usage</p>
              <p className="font-semibold">{insight.competitor_usage_count}</p>
            </div>
            <div className="rounded-lg border border-border p-3">
              <p className="text-xs text-muted-foreground">My usage</p>
              <p className="font-semibold">{insight.user_usage_count}</p>
            </div>
            <div className="rounded-lg border border-border p-3">
              <p className="text-xs text-muted-foreground">Est. demand</p>
              <EstimateBadge value={insight.search_volume_estimate} />
            </div>
            <div className="rounded-lg border border-border p-3">
              <p className="text-xs text-muted-foreground">Competition</p>
              <EstimateBadge value={insight.competition_estimate} />
            </div>
          </div>

          <Section title="Suggested action" content={insight.suggested_action} />

          {insight.example_competitor_listings.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Competitor listings</p>
              <ul className="space-y-1 text-xs text-muted-foreground">
                {insight.example_competitor_listings.map((l) => (
                  <li key={l.url || l.title}>• {l.title} ({l.shop_name})</li>
                ))}
              </ul>
            </div>
          )}

          {insight.example_user_listings.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">My listings</p>
              <ul className="space-y-1 text-xs text-muted-foreground">
                {insight.example_user_listings.map((l) => (
                  <li key={l.url || l.title}>• {l.title}</li>
                ))}
              </ul>
            </div>
          )}

          {insight.related_tags.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Related tags</p>
              <div className="flex flex-wrap gap-1.5">
                {insight.related_tags.map((t) => (
                  <span key={t} className="rounded-full border border-border px-2 py-0.5 text-xs">{t}</span>
                ))}
              </div>
            </div>
          )}

          {insight.suggested_title_phrases && insight.suggested_title_phrases.length > 0 && (
            <Section title="Suggested title phrases" content={insight.suggested_title_phrases.join("; ")} />
          )}

          {insight.suggested_etsy_tags && insight.suggested_etsy_tags.length > 0 && (
            <Section title="Suggested Etsy tags" content={insight.suggested_etsy_tags.join(", ")} />
          )}

          {insight.suggested_description_phrase && (
            <Section title="Suggested description phrase" content={insight.suggested_description_phrase} />
          )}

          {insight.pricing_context && (
            <Section title="Pricing context" content={insight.pricing_context} />
          )}
        </div>
      </div>
    </div>
  );
}

function Section({ title, content }: { title: string; content: string }) {
  return (
    <div>
      <p className="text-sm font-medium mb-1">{title}</p>
      <p className="text-sm text-muted-foreground">{content}</p>
    </div>
  );
}

function LegacyKeywordFallback({ summary }: { summary: NonNullable<AnalysisDetail["keyword_summary"]> }) {
  const keywords = summary.top_keywords || [];
  const tags = summary.common_tags || [];
  const missing = summary.missing_opportunities || [];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-4 w-4 text-primary" />
            Your shop keywords
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <TagList title="Top keywords" items={keywords.map((k) => `${k.keyword} (${k.count})`)} />
          <TagList title="Common tags" items={tags.map((t) => t.tag)} />
          {missing.length > 0 && <TagList title="Missing opportunities" items={missing} warning />}
        </CardContent>
      </Card>
    </div>
  );
}

function TagList({ title, items, warning }: { title: string; items: string[]; warning?: boolean }) {
  return (
    <div>
      <p className="text-sm font-medium mb-2">{title}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className={
              warning
                ? "rounded-lg border border-dashed border-amber-300 bg-amber-50 px-2.5 py-1 text-sm text-amber-900"
                : "rounded-lg border border-border bg-muted/50 px-2.5 py-1 text-sm"
            }
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
