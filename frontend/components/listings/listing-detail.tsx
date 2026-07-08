"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import type { Listing } from "@/lib/types";
import { X } from "lucide-react";

export function ListingDetail({ listing, onClose }: { listing: Listing; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-start justify-between">
          <div>
            <CardTitle className="text-lg">{listing.title}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{listing.shop_name}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}><X className="h-4 w-4" /></Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {listing.image_url && (
            <img src={listing.image_url} alt={listing.title} className="rounded-lg w-full max-h-48 object-cover" />
          )}
          <div className="grid grid-cols-3 gap-4">
            <div><p className="text-sm text-muted-foreground">Price</p><p className="font-semibold">{formatCurrency(listing.price)}</p></div>
            <div><p className="text-sm text-muted-foreground">Rating</p><p className="font-semibold">{listing.rating || "—"}</p></div>
            <div><p className="text-sm text-muted-foreground">Reviews</p><p className="font-semibold">{listing.review_count || "—"}</p></div>
          </div>
          {listing.description && (
            <div>
              <p className="text-sm font-medium mb-1">Description</p>
              <p className="text-sm text-muted-foreground">{listing.description}</p>
            </div>
          )}
          {listing.tags.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Tags</p>
              <div className="flex flex-wrap gap-1">
                {listing.tags.map((t) => <Badge key={t} variant="outline">{t}</Badge>)}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
