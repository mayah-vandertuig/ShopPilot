"use client";

import { Shell } from "@/components/layout/shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings, Key, Globe, Bot } from "lucide-react";

export default function SettingsPage() {
  return (
    <Shell title="Settings" subtitle="Environment and integration configuration">
      <div className="mx-auto max-w-3xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-4 w-4 text-primary" />
              Application settings
            </CardTitle>
            <CardDescription>Configure API keys and integrations in your <code className="text-xs bg-muted px-1.5 py-0.5 rounded">.env</code> file.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SettingRow icon={Globe} title="Bright Data" description="BRIGHT_DATA_API_KEY or BRIGHTDATA_API_TOKEN" badge="Required for analyses" />
            <SettingRow icon={Bot} title="OpenAI" description="OPENAI_API_KEY for AI recommendations and Q&A" badge="Required for AI" />
            <SettingRow icon={Key} title="Codex agents" description="CODEX_AGENTS_ENABLED=true to enable engineering tools" badge="Optional" />
          </CardContent>
        </Card>
        <div className="alert-info">
          Restart the backend after changing environment variables for changes to take effect.
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
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  badge: string;
}) {
  return (
    <div className="flex items-start gap-4 rounded-xl border border-border bg-muted/20 p-4">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-medium text-foreground">{title}</p>
          <Badge variant="outline">{badge}</Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
    </div>
  );
}
