"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CodexStatusCard } from "@/components/codex/codex-status-card";
import { getCodexStatus, getSettingsStatus } from "@/lib/api";
import type { CodexStatus, SettingsStatus } from "@/lib/types";
import { Settings, Key, Globe, Bot, Database, Server } from "lucide-react";

export default function SettingsPage() {
  const [codexStatus, setCodexStatus] = useState<CodexStatus | null>(null);
  const [settings, setSettings] = useState<SettingsStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getCodexStatus(), getSettingsStatus()])
      .then(([codex, appSettings]) => {
        setCodexStatus(codex);
        setSettings(appSettings);
      })
      .catch(() => {
        setCodexStatus(null);
        setSettings(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell title="Settings" subtitle="Environment, localization, and integration configuration">
      <div className="mx-auto max-w-3xl space-y-6">
        {loading ? (
          <Skeleton className="h-48 w-full rounded-xl" />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-4 w-4 text-primary" />
                Application defaults
              </CardTitle>
              <CardDescription>Localization and runtime defaults used for new analyses.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2">
              <SettingValue label="Default country" value={settings?.default_country || "US"} />
              <SettingValue label="Default language" value={settings?.default_language || "en-US"} />
              <SettingValue label="Default locale" value={settings?.default_locale || "en_US"} />
              <SettingValue label="Default currency" value={settings?.default_currency || "USD"} />
              <SettingValue label="Data mode" value={settings?.data_mode === "live" ? "Bright Data live" : "Bright Data unavailable"} />
              <SettingValue label="Database status" value={settings?.database_status || "unknown"} />
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Integration status</CardTitle>
            <CardDescription>Keys are never displayed — only configured / not configured.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SettingRow icon={Globe} title="Bright Data" description="BRIGHT_DATA_API_KEY or BRIGHTDATA_API_TOKEN" configured={settings?.bright_data_configured} required />
            <SettingRow icon={Bot} title="OpenAI" description="OPENAI_API_KEY for AI recommendations and Q&A" configured={settings?.openai_configured} />
            <SettingRow icon={Key} title="Codex agents" description="CODEX_AGENTS_ENABLED=true" configured={settings?.codex_enabled} />
            <SettingRow icon={Server} title="Backend API URL" description="FastAPI service used by the frontend" configured value={settings?.backend_api_url || "http://localhost:8000"} />
            <SettingRow icon={Database} title="Database" description="SQLite persistence for analyses and listings" configured value={settings?.database_status || "unknown"} />
          </CardContent>
        </Card>

        <CodexStatusCard status={codexStatus} />

        <Card>
          <CardHeader>
            <CardTitle>Codex safety settings</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge variant={codexStatus?.require_human_review ? "success" : "warning"}>
              Human review: {codexStatus?.require_human_review ? "Required" : "Optional"}
            </Badge>
            <Badge variant={codexStatus?.allow_file_patch ? "warning" : "success"}>
              File patching: {codexStatus?.allow_file_patch ? "Allowed" : "Disabled"}
            </Badge>
            <Badge variant="outline">Mode: {codexStatus?.mode || "subprocess"}</Badge>
          </CardContent>
        </Card>

        <div className="alert-info">
          Configure variables in <code className="text-xs bg-muted px-1.5 py-0.5 rounded">.env</code> at the project root, then restart the backend. Bright Data is required for live marketplace scraping.
        </div>
      </div>
    </Shell>
  );
}

function SettingValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-muted/20 p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium text-foreground mt-1">{value}</p>
    </div>
  );
}

function SettingRow({
  icon: Icon,
  title,
  description,
  configured,
  required = false,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  configured?: boolean;
  required?: boolean;
  value?: string;
}) {
  const badge = value
    ? value
    : configured
      ? "Configured"
      : required
        ? "Not configured"
        : "Optional / not set";

  return (
    <div className="flex items-start gap-4 rounded-xl border border-border bg-muted/20 p-4">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-medium text-foreground">{title}</p>
          <Badge variant={configured || value ? "success" : required ? "warning" : "outline"}>{badge}</Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
    </div>
  );
}
