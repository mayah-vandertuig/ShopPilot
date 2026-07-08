import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShopPilot — AI Marketplace Intelligence",
  description: "AI-powered marketplace intelligence dashboard for online sellers",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
