"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { SchoolCard } from "@/components/schools/SchoolCard";
import { Skeleton } from "@/components/ui/skeleton";
import { listSchools } from "@/lib/api/schools";
import type { SchoolListItem } from "@/lib/types";

const FEATURED_ACARA_IDS_NAMES = ["Somerset College", "All Saints Anglican School"];

export default function SchoolsPage() {
  const { getToken } = useAuth();
  const [schools, setSchools] = useState<SchoolListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [sectorFilter, setSectorFilter] = useState<string>("All");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await listSchools(token);
        if (!cancelled) setSchools(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken]);

  const featured = schools.filter((s) => FEATURED_ACARA_IDS_NAMES.includes(s.name));
  const rest = schools.filter((s) => !FEATURED_ACARA_IDS_NAMES.includes(s.name));

  const filtered = sectorFilter === "All"
    ? rest
    : rest.filter((s) => s.sector === sectorFilter);

  const sectors = ["All", ...Array.from(new Set(schools.map((s) => s.sector))).sort()];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-semibold">Schools on the Gold Coast</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          {schools.length} schools in your search area
        </p>
      </div>

      {/* Featured schools */}
      {featured.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-base font-semibold text-muted-foreground uppercase tracking-wide text-xs">
            Your Shortlisted Schools
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {featured.map((school) => (
              <SchoolCard key={school.id} school={school} featured />
            ))}
          </div>
        </div>
      )}

      {/* Filter bar */}
      <div className="flex gap-2 flex-wrap">
        {sectors.map((sector) => (
          <button
            key={sector}
            onClick={() => setSectorFilter(sector)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors capitalize ${
              sectorFilter === sector
                ? "bg-foreground text-background border-foreground"
                : "border-border text-muted-foreground hover:text-foreground hover:border-foreground"
            }`}
          >
            {sector === "All" ? "All Schools" : sector}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-52 rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-muted-foreground">No schools match this filter.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((school) => (
            <SchoolCard key={school.id} school={school} />
          ))}
        </div>
      )}
    </div>
  );
}
