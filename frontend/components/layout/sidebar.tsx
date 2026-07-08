"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, PlusCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { getAnalysisNav, getAnalysisViewNav, getHomeNav, isNavActive, utilityNav } from "@/lib/navigation";

export function Sidebar() {
  const pathname = usePathname();
  const analysisMatch = pathname.match(/^\/analyses\/(\d+)/);
  const analysisId = analysisMatch ? Number(analysisMatch[1]) : null;
  const mainNav = analysisId ? getAnalysisNav(analysisId) : getHomeNav();

  const NavLink = ({
    href,
    label,
    icon: Icon,
    active,
    disabled,
  }: {
    href: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    active: boolean;
    disabled?: boolean;
  }) => {
    if (disabled) {
      return (
        <span className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground/50 cursor-not-allowed">
          <Icon className="h-4 w-4 shrink-0" />
          {label}
        </span>
      );
    }
    return (
      <Link
        href={href}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
          active
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-muted-foreground hover:bg-white hover:text-foreground"
        )}
      >
        <Icon className="h-4 w-4 shrink-0" />
        {label}
      </Link>
    );
  };

  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border bg-[#F1F5F9]/60 min-h-screen">
      <div className="flex h-16 items-center gap-2.5 border-b border-border px-5 bg-white">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <BarChart3 className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-bold text-foreground leading-none">ShopPilot</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">Marketplace Intel</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        <div>
          <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {analysisId ? "Analysis" : "Main"}
          </p>
          <div className="space-y-0.5">
            {analysisId && (
              <NavLink
                href="/"
                label="New analysis"
                icon={PlusCircle}
                active={false}
              />
            )}
            {mainNav.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                label={item.label}
                icon={item.icon}
                active={isNavActive(pathname, item.href, item.matchExact)}
              />
            ))}
          </div>
        </div>

        {!analysisId && (
          <div>
            <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Analysis views</p>
            <div className="space-y-0.5">
              {getAnalysisViewNav().map((item) => (
                <NavLink key={item.label} href="#" label={item.label} icon={item.icon} active={false} disabled />
              ))}
            </div>
            <p className="px-3 mt-3 text-[11px] text-muted-foreground leading-relaxed">Run an analysis to unlock these pages.</p>
          </div>
        )}

        <div>
          <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Tools</p>
          <div className="space-y-0.5">
            {utilityNav.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                label={item.label}
                icon={item.icon}
                active={isNavActive(pathname, item.href)}
              />
            ))}
          </div>
        </div>
      </nav>
    </aside>
  );
}
