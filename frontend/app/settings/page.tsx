"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CodexStatusCard } from "@/components/codex/codex-status-card";
import { getCodexStatus } from "@/lib/api";
import type { CodexStatus } from "@/lib/types";
import { Settings, Key, Globe, Bot } from "lucide-react";

export default function SettingsPage() {
  const [codexStatus, setCodexStatus] = useState<CodexStatus | null>(null);

  useEffect(() => {
    getCodexStatus()
      .then(setCodexStatus)
      .catch(() => setCodexStatus(null));
  }, []);

  return (
    <Shell title="Settings" subtitle="Environment and integration configuration">
      <div className="mx-auto max-w-3xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-4 w-4 text-primary" />
              Application settings
            </CardTitle>
            <CardDescription>Configure API keys and integrations in your <code className="text-xs bg-muted px-1.5 py-0.5 rounded">.env</code> file at the project root.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SettingRow icon={Globe} title="Bright Data" description="BRIGHT_DATA_API_KEY or BRIGHTDATA_API_TOKEN" badge="Required for analyses" />
            <SettingRow icon={Bot} title="OpenAI" description="OPENAI_API_KEY for AI recommendations and Q&A" badge="Required for AI" />
            <SettingRow
              icon={Key}
              title="Codex agents"
              description="CODEX_AGENTS_ENABLED=true — adapter repair, extraction QA, test generation"
              badge={codexStatus?.enabled ? "Enabled" : "Disabled"}
              badgeVariant={codexStatus?.enabled ? "success" : "outline"}
            />
          </CardContent>
        </Card>

        <CodexStatusCard status={codexStatus} />

        <div className="alert-info">
          Restart the backend after changing environment variables. Codex tools are at <strong>Codex Tools</strong> in the sidebar.
        </div>
      </div>
    </Shell>
  );
}

function SettingRow({
  icon: Icon,
  title,
  description,
  badge,
  badgeVariant = "outline",
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  badge: string;
  badgeVariant?: "outline" | "success";
}) {
  return (
    <div className="flex items-start gap-4 rounded-xl border border-border bg-muted/20 p-4">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-medium text-foreground">{title}</p>
          <Badge variant={badgeVariant}>{badge}</Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
    </div>
  );
}
