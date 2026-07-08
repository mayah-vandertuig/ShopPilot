"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Home, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/codex", label: "Codex Tools", icon: Wrench },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-border bg-white min-h-screen">
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <BarChart3 className="h-6 w-6 text-primary" />
        <span className="text-xl font-bold">ShopPilot</span>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border">
        <p className="text-xs text-muted-foreground">AI Commerce Intelligence</p>
      </div>
    </aside>
  );
}
