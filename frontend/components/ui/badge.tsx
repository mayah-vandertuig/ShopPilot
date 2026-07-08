import { cn } from "@/lib/utils";

const variants = {
  default: "bg-primary/10 text-primary",
  success: "bg-emerald-50 text-success border border-emerald-200",
  warning: "bg-amber-50 text-warning border border-amber-200",
  danger: "bg-red-50 text-danger border border-red-200",
  outline: "border border-border text-muted-foreground bg-white",
  platform: "bg-slate-100 text-slate-700 border border-slate-200",
  live: "bg-emerald-50 text-success border border-emerald-200",
  mock: "bg-amber-50 text-warning border border-amber-200",
  fallback: "bg-sky-50 text-sky-700 border border-sky-200",
};

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export function dataSourceBadgeVariant(source?: string): keyof typeof variants {
  if (source === "live") return "live";
  if (source === "mock") return "mock";
  if (source === "fallback") return "fallback";
  return "outline";
}

export function dataSourceLabel(source?: string): string {
  if (source === "live") return "Bright Data · Live";
  if (source === "mock") return "Mock Data";
  if (source === "fallback") return "Fallback";
  if (!source) return "Unknown";
  return source.charAt(0).toUpperCase() + source.slice(1);
}
