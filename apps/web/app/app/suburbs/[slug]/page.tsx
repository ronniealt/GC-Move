"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreRing } from "@/components/score/ScoreRing";
import { getSuburb } from "@/lib/api/suburbs";
import type { SuburbDetailResponse } from "@/lib/types";

const TIER_VARIANTS: Record<string, string> = {
  Premium: "bg-teal-500 text-white",
  Good: "bg-blue-500 text-white",
  Acceptable: "bg-amber-500 text-white",
};

function ScoreItem({ label, score }: { label: string; score: number | null | undefined }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <ScoreRing score={score ?? null} size={56} strokeWidth={5} />
      <span className="text-xs text-muted-foreground text-center">{label}</span>
    </div>
  );
}

export default function SuburbDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const slug = params.slug as string;

  const [suburb, setSuburb] = useState<SuburbDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await getSuburb(slug, token);
        if (!cancelled) setSuburb(data);
      } catch (e: unknown) {
        if (!cancelled) setNotFound(true);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [slug, getToken]);

  if (loading) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 rounded-xl" />
        <Skeleton className="h-48 rounded-xl" />
      </div>
    );
  }

  if (notFound || !suburb) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <p className="text-muted-foreground">Suburb not found.</p>
        <button onClick={() => router.back()} className="mt-4 text-sm text-teal-600 hover:underline flex items-center gap-1">
          <ArrowLeft size={14} /> Back
        </button>
      </div>
    );
  }

  const tierVariant = TIER_VARIANTS[suburb.tier_label] ?? "bg-muted";

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      {/* Back */}
      <button
        onClick={() => router.push("/app/suburbs")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        <ArrowLeft size={14} /> All Suburbs
      </button>

      {/* Hero */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-semibold">{suburb.name}</h1>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${tierVariant}`}>
            {suburb.tier_label}
          </span>
        </div>
        <p className="text-muted-foreground text-sm">
          {suburb.postcode} · {suburb.lga ?? "Gold Coast City Council"}
        </p>
      </div>

      {/* Scores */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Suburb Scores</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-8 flex-wrap">
            <ScoreItem label="Community" score={suburb.metrics?.community_score} />
            <ScoreItem label="Lifestyle" score={suburb.lifestyle?.lifestyle_score} />
            <ScoreItem label="Beach Access" score={suburb.lifestyle?.beach_access_score} />
            <ScoreItem label="Café & Dining" score={suburb.lifestyle?.cafe_dining_score} />
            <ScoreItem label="Wellness" score={suburb.lifestyle?.wellness_infrastructure_score} />
            <ScoreItem label="Shopping" score={suburb.lifestyle?.shopping_score} />
          </div>
        </CardContent>
      </Card>

      {/* Community metrics */}
      {suburb.metrics && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Community Profile</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {suburb.metrics.owner_occupier_rate !== null && (
              <div>
                <p className="text-xs text-muted-foreground">Owner Occupiers</p>
                <p className="text-sm font-medium">{suburb.metrics.owner_occupier_rate?.toFixed(0)}%</p>
              </div>
            )}
            {suburb.metrics.family_density_pct !== null && (
              <div>
                <p className="text-xs text-muted-foreground">Family Households</p>
                <p className="text-sm font-medium">{suburb.metrics.family_density_pct?.toFixed(0)}%</p>
              </div>
            )}
            {suburb.metrics.median_weekly_household_income_aud !== null && (
              <div>
                <p className="text-xs text-muted-foreground">Median Weekly Income</p>
                <p className="text-sm font-medium">
                  ${suburb.metrics.median_weekly_household_income_aud?.toLocaleString()}
                </p>
              </div>
            )}
            {suburb.metrics.crime_index !== null && (
              <div>
                <p className="text-xs text-muted-foreground">Crime Index</p>
                <p className="text-sm font-medium">{suburb.metrics.crime_index?.toFixed(1)}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Lifestyle assets */}
      {suburb.lifestyle && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Lifestyle Infrastructure</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {suburb.lifestyle.beach_access_minutes !== null && (
              <div>
                <p className="text-xs text-muted-foreground">Beach</p>
                <p className="text-sm font-medium">{suburb.lifestyle.beach_access_minutes} min</p>
              </div>
            )}
            {suburb.lifestyle.burleigh_drive_minutes !== null && (
              <div>
                <p className="text-xs text-muted-foreground">To Burleigh</p>
                <p className="text-sm font-medium">{suburb.lifestyle.burleigh_drive_minutes} min</p>
              </div>
            )}
            {suburb.lifestyle.travel_to_broadbeach_min !== null && (
              <div>
                <p className="text-xs text-muted-foreground">To Broadbeach</p>
                <p className="text-sm font-medium">{suburb.lifestyle.travel_to_broadbeach_min} min</p>
              </div>
            )}
            {suburb.lifestyle.travel_to_airport_min !== null && (
              <div>
                <p className="text-xs text-muted-foreground">To Airport</p>
                <p className="text-sm font-medium">{suburb.lifestyle.travel_to_airport_min} min</p>
              </div>
            )}
            <div>
              <p className="text-xs text-muted-foreground">Cafés & Restaurants</p>
              <p className="text-sm font-medium">{suburb.lifestyle.cafe_restaurant_count}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Gyms</p>
              <p className="text-sm font-medium">{suburb.lifestyle.gym_fitness_count}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Parks</p>
              <p className="text-sm font-medium">{suburb.lifestyle.park_reserve_count}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Supermarkets</p>
              <p className="text-sm font-medium">{suburb.lifestyle.supermarket_count}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schools */}
      {suburb.schools.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Schools in Catchment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {suburb.schools.map((school) => (
              <div key={school.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div>
                  <p className="text-sm font-medium">{school.name}</p>
                  <p className="text-xs text-muted-foreground">{school.address_suburb}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs capitalize">{school.sector}</Badge>
                  {school.year_range && (
                    <span className="text-xs text-muted-foreground">{school.year_range}</span>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
