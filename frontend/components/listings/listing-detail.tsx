"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import type { Listing } from "@/lib/types";
import { X, ExternalLink } from "lucide-react";

export function ListingDetail({ listing, onClose }: { listing: Listing; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-foreground/20 backdrop-blur-sm" onClick={onClose}>
      <div
        className="h-full w-full max-w-lg overflow-y-auto bg-white shadow-2xl border-l border-border"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 flex items-center justify-between border-b border-border bg-white px-6 py-4">
          <h3 className="font-semibold text-foreground">Listing details</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="p-6 space-y-6">
          {listing.image_url && (
            <div className="flex w-full items-center justify-center overflow-hidden rounded-xl border border-border bg-muted/20 p-3">
              <img
                src={listing.image_url}
                alt={listing.title}
                className="max-h-80 w-full object-contain"
              />
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
                {listing.tags.map((t) => (
                  <Badge key={t} variant="outline">{t}</Badge>
                ))}
              </div>
            </div>
          )}
          {listing.url && (
            <a
              href={listing.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View on marketplace <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
