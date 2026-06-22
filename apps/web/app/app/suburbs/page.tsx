"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { SuburbCard } from "@/components/suburbs/SuburbCard";
import { Skeleton } from "@/components/ui/skeleton";
import { listSuburbs } from "@/lib/api/suburbs";
import type { SuburbListItem } from "@/lib/types";

type TierFilter = "All" | "A" | "B" | "C";

const TIER_LABELS: Record<TierFilter, string> = {
  All: "All Suburbs",
  A: "Premium",
  B: "Good",
  C: "Acceptable",
};

export default function SuburbsPage() {
  const { getToken } = useAuth();
  const [suburbs, setSuburbs] = useState<SuburbListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [tierFilter, setTierFilter] = useState<TierFilter>("All");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await listSuburbs(token);
        if (!cancelled) setSuburbs(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken]);

  const filtered = tierFilter === "All"
    ? suburbs
    : suburbs.filter((s) => s.tier === tierFilter);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Gold Coast Suburbs</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          {suburbs.length} suburbs scored for your family
        </p>
      </div>

      <div className="flex gap-2">
        {(["All", "A", "B", "C"] as TierFilter[]).map((tier) => (
          <button
            key={tier}
            onClick={() => setTierFilter(tier)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              tierFilter === tier
                ? "bg-foreground text-background border-foreground"
                : "border-border text-muted-foreground hover:text-foreground hover:border-foreground"
            }`}
          >
            {TIER_LABELS[tier]}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-muted-foreground">No suburbs match this filter.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((suburb) => (
            <SuburbCard key={suburb.id} suburb={suburb} />
          ))}
        </div>
      )}
    </div>
  );
}
