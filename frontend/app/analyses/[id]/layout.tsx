import { AnalysisLayout } from "@/lib/analysis-context";

export default function AnalysisRootLayout({ children }: { children: React.ReactNode }) {
  return <AnalysisLayout>{children}</AnalysisLayout>;
}
