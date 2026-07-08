"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { createAnalysis } from "@/lib/api";
import { normalizeEtsyShopInput } from "@/lib/etsy";
import { COUNTRIES, CURRENCIES } from "@/lib/types";
import { Loader2 } from "lucide-react";

const SHOP_NAME_STORAGE_KEY = "shoppilot_last_shop_name";

type ShopAnalysisFormProps = {
  initialShopName?: string;
  initialCountry?: string;
  initialCurrency?: string;
  compact?: boolean;
  onSuccess?: () => void;
};

export function ShopAnalysisForm({
  initialShopName = "",
  initialCountry = "US",
  initialCurrency = "USD",
  compact = false,
  onSuccess,
}: ShopAnalysisFormProps) {
  const router = useRouter();
  const [shopName, setShopName] = useState(initialShopName);
  const [country, setCountry] = useState(initialCountry);
  const [currency, setCurrency] = useState(initialCurrency);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialShopName) {
      setShopName(initialShopName);
      return;
    }
    const saved = window.localStorage.getItem(SHOP_NAME_STORAGE_KEY);
    if (saved) setShopName(saved);
  }, [initialShopName]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const normalized = normalizeEtsyShopInput(shopName);
    if (!normalized) {
      setError("Enter an Etsy shop name to analyze.");
      return;
    }

    setShopName(normalized);
    setLoading(true);
    setError(null);

    try {
      const result = await createAnalysis({
        platform: "etsy",
        input_type: "shop_name",
        input_value: normalized,
        country,
        currency,
      });
      window.localStorage.setItem(SHOP_NAME_STORAGE_KEY, normalized);
      onSuccess?.();
      router.push(`/analyses/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="flex-1 min-w-0">
            <label htmlFor="etsy-shop-name-compact" className="sr-only">
              Etsy shop name
            </label>
            <Input
              id="etsy-shop-name-compact"
              name="shopName"
              type="text"
              autoComplete="off"
              spellCheck={false}
              value={shopName}
              onChange={(e) => setShopName(e.target.value)}
              onBlur={(e) => setShopName(normalizeEtsyShopInput(e.target.value))}
              placeholder="Enter shop name or paste Etsy shop URL"
              disabled={loading}
              className="w-full"
            />
          </div>
          <Button type="submit" disabled={loading || !shopName.trim()}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Analyze shop"}
          </Button>
        </div>
        {error && <div className="alert-danger">{error}</div>}
      </form>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <Field label="Etsy shop name" htmlFor="etsy-shop-name">
          <Input
            id="etsy-shop-name"
            name="shopName"
            type="text"
            autoComplete="off"
            spellCheck={false}
            value={shopName}
            onChange={(e) => setShopName(e.target.value)}
            onBlur={(e) => setShopName(normalizeEtsyShopInput(e.target.value))}
            placeholder="ArtStudioCo"
            disabled={loading}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
            Paste the shop slug, full shop URL, or @handle — we&apos;ll fetch the shop for you.
          </p>
        </Field>

        <Field label="Country" htmlFor="etsy-country">
          <Select id="etsy-country" value={country} onChange={(e) => setCountry(e.target.value)} disabled={loading}>
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Currency" htmlFor="etsy-currency">
          <Select id="etsy-currency" value={currency} onChange={(e) => setCurrency(e.target.value)} disabled={loading}>
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </Select>
        </Field>

        <div className="flex items-end md:col-span-2 lg:col-span-3">
          <Button type="submit" disabled={loading || !shopName.trim()} className="w-full sm:w-auto" size="lg">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Analyzing...
              </>
            ) : (
              "Analyze shop"
            )}
          </Button>
        </div>
      </div>
      {error && <div className="alert-danger">{error}</div>}
    </form>
  );
}

function Field({
  label,
  htmlFor,
  children,
  className,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={className}>
      <label htmlFor={htmlFor} className="text-sm font-medium text-foreground mb-1.5 block">
        {label}
      </label>
      {children}
    </div>
  );
}
