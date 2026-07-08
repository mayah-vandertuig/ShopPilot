import {
  LayoutDashboard,
  DollarSign,
  Users,
  Hash,
  TrendingUp,
  List,
  Sparkles,
  Wrench,
  Settings,
  type LucideIcon,
} from "lucide-react";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  matchExact?: boolean;
};

export const utilityNav: NavItem[] = [
  { label: "Codex Tools", href: "/codex", icon: Wrench },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function getAnalysisNav(analysisId: number): NavItem[] {
  const base = `/analyses/${analysisId}`;
  return [
    { label: "Overview", href: base, icon: LayoutDashboard, matchExact: true },
    { label: "Pricing", href: `${base}/pricing`, icon: DollarSign },
    { label: "Competitors", href: `${base}/competitors`, icon: Users },
    { label: "Keywords", href: `${base}/keywords`, icon: Hash },
    { label: "Trends", href: `${base}/trends`, icon: TrendingUp },
    { label: "Listings", href: `${base}/listings`, icon: List },
    { label: "AI Advisor", href: `${base}/ai-advisor`, icon: Sparkles },
  ];
}

export function getHomeNav(): NavItem[] {
  return [{ label: "Overview", href: "/", icon: LayoutDashboard, matchExact: true }];
}

export function getAnalysisViewNav(): Pick<NavItem, "label" | "icon">[] {
  return getAnalysisNav(0).slice(1).map(({ label, icon }) => ({ label, icon }));
}

export function isNavActive(pathname: string, href: string, matchExact?: boolean) {
  if (matchExact) return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}
