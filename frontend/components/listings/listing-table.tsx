"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatCurrency } from "@/lib/utils";
import type { Listing } from "@/lib/types";
import { ListingDetail } from "./listing-detail";

export function ListingTable({ listings }: { listings: Listing[] }) {
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Listing | null>(null);

  const filtered = listings.filter(
    (l) =>
      l.title.toLowerCase().includes(filter.toLowerCase()) ||
      l.shop_name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Listings ({listings.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Filter by title or shop..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="mb-4 max-w-sm"
          />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted-foreground">
                  <th className="pb-3 font-medium">Title</th>
                  <th className="pb-3 font-medium">Shop</th>
                  <th className="pb-3 font-medium">Price</th>
                  <th className="pb-3 font-medium">Rating</th>
                  <th className="pb-3 font-medium">Reviews</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((l) => (
                  <tr
                    key={l.id}
                    className="border-b border-border/50 cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelected(l)}
                  >
                    <td className="py-3 max-w-xs truncate font-medium">{l.title}</td>
                    <td className="py-3">{l.shop_name}</td>
                    <td className="py-3">{formatCurrency(l.price, l.currency)}</td>
                    <td className="py-3">{l.rating > 0 ? l.rating.toFixed(1) : "—"}</td>
                    <td className="py-3">{l.review_count || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      {selected && <ListingDetail listing={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
