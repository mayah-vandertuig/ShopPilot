"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import type { Listing, ListingIssue } from "@/lib/types";
import { X, ExternalLink } from "lucide-react";

export function ListingDetail({
  listing,
  issues = [],
  recommendations = [],
  isUserListing = true,
  onClose,
}: {
  listing: Listing;
  issues?: ListingIssue[];
  recommendations?: Array<{ recommendation: string; category: string }>;
  isUserListing?: boolean;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-y-0 right-0 left-0 lg:left-64 z-40 flex justify-end bg-foreground/20 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="h-full w-full max-w-lg overflow-y-auto bg-white shadow-2xl border-l border-border"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 flex items-center justify-between border-b border-border bg-white px-6 py-4">
          <div>
            <h3 className="font-semibold text-foreground">Listing details</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isUserListing ? "Your listing" : "Competitor listing"} · {listing.platform}
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="p-6 space-y-6">
          {listing.image_url && (
            <div className="flex w-full items-center justify-center overflow-hidden rounded-xl border border-border bg-muted/20 p-3">
              <img src={listing.image_url} alt={listing.title} className="max-h-80 w-full object-contain" />
            </div>
          )}
          <div>
            <h4 className="text-lg font-semibold text-foreground leading-snug">{listing.title}</h4>
            <p className="text-sm text-muted-foreground mt-1">{listing.shop_name}</p>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Price", value: formatCurrency(listing.price, listing.currency) },
              { label: "Rating", value: listing.rating > 0 ? listing.rating.toFixed(1) : "—" },
              { label: "Reviews", value: listing.review_count || "—" },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-border bg-muted/30 p-3 text-center">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="font-semibold text-foreground mt-1">{item.value}</p>
              </div>
            ))}
          </div>
          {listing.description && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-2">Description</p>
              <p className="text-sm text-muted-foreground leading-relaxed">{listing.description}</p>
            </div>
          )}
          {listing.tags.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-2">Tags</p>
              <div className="flex flex-wrap gap-1.5">
                {listing.tags.map((tag) => (
                  <Badge key={tag} variant="outline">{tag}</Badge>
                ))}
              </div>
            </div>
          )}
          {listing.detected_keywords.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-2">Detected keywords</p>
              <div className="flex flex-wrap gap-1.5">
                {listing.detected_keywords.map((keyword) => (
                  <Badge key={keyword} variant="outline">{keyword}</Badge>
                ))}
              </div>
            </div>
          )}
          {issues.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-2">Issues</p>
              <div className="space-y-2">
                {issues.map((issue) => (
                  <div key={issue.id} className="rounded-lg border border-border bg-muted/20 p-3 text-sm">
                    <Badge variant={issue.severity === "high" ? "danger" : issue.severity === "medium" ? "warning" : "outline"}>
                      {issue.severity}
                    </Badge>
                    <p className="font-medium text-foreground mt-2">{issue.issue}</p>
                    <p className="text-muted-foreground mt-1">{issue.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {recommendations.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-2">AI suggestions</p>
              <div className="space-y-2">
                {recommendations.map((rec, index) => (
                  <div key={`${rec.category}-${index}`} className="rounded-lg border border-border p-3 text-sm">
                    <Badge variant="outline">{rec.category}</Badge>
                    <p className="text-foreground mt-2">{rec.recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {!isUserListing && (
            <div className="rounded-xl border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
              Competitor context: compare this listing&apos;s price, keywords, and reviews against your shop on the Competitors and Keywords pages.
            </div>
          )}
          {listing.url && (
            <a
              href={listing.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View source listing <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
