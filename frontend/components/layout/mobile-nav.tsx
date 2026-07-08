"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { getAnalysisNav, isNavActive } from "@/lib/navigation";

export function MobileNav() {
  const pathname = usePathname();
  const analysisMatch = pathname.match(/^\/analyses\/(\d+)/);
  const analysisId = analysisMatch ? Number(analysisMatch[1]) : null;

  if (!analysisId) {
    return null;
  }

  const items = getAnalysisNav(analysisId);

  return (
    <nav className="lg:hidden border-b border-border bg-white overflow-x-auto">
      <div className="flex gap-1 px-3 py-2 min-w-max">
        {items.map((item) => {
          const active = isNavActive(pathname, item.href, item.matchExact);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "rounded-lg px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
