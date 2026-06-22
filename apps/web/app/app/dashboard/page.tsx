"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PropertyCard } from "@/components/property/PropertyCard";
import { getDashboard } from "@/lib/api/dashboard";
import { getMyFamily } from "@/lib/api/families";
import type { DashboardResponse, FamilyResponse } from "@/lib/types";

function formatDateTime(dt: string | null) {
  if (!dt) return "TBD";
  return new Date(dt).toLocaleString("en-AU", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function DashboardPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();

  const [family, setFamily] = useState<FamilyResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!isLoaded) return;
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const [fam, dash] = await Promise.all([getMyFamily(token), getDashboard(token)]);
        if (!cancelled) {
          setFamily(fam);
          setDashboard(dash);
        }
      } catch {
        // family may not exist yet
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [getToken, isLoaded]);

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-semibold">
          {greeting()}{family ? `, ${family.display_name}` : " there"}
        </h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Here&apos;s what&apos;s happening with your move.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {loading ? (
          <>
            <Skeleton className="h-24 rounded-xl" />
            <Skeleton className="h-24 rounded-xl" />
            <Skeleton className="h-24 rounded-xl" />
          </>
        ) : (
          <>
            <Card className="p-5">
              <p className="text-sm text-muted-foreground">Properties Reviewed</p>
              <p className="text-3xl font-bold mt-1">{dashboard?.properties_reviewed ?? 0}</p>
            </Card>
            <Card className="p-5">
              <p className="text-sm text-muted-foreground">New This Week</p>
              <p className="text-3xl font-bold mt-1">{dashboard?.new_this_week ?? 0}</p>
            </Card>
            <Card className="p-5">
              <p className="text-sm text-muted-foreground">On Shortlist</p>
              <p className="text-3xl font-bold mt-1">{dashboard?.shortlist_count ?? 0}</p>
            </Card>
          </>
        )}
      </div>

      {/* Top Recommendations */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Properties to look at today</h2>

        {loading ? (
          <div className="flex gap-4 overflow-x-auto pb-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-72 w-72 rounded-xl shrink-0" />
            ))}
          </div>
        ) : dashboard && dashboard.top_recommendations.length > 0 ? (
          <div className="flex gap-4 overflow-x-auto pb-2">
            {dashboard.top_recommendations.map((prop) => (
              <PropertyCard
                key={prop.id}
                property={prop}
                onClick={() => router.push(`/app/properties/${prop.id}`)}
              />
            ))}
          </div>
        ) : (
          <Card className="p-10 text-center">
            <p className="text-muted-foreground mb-4">
              Add your first property to get started.
            </p>
            <Link
              href="/app/properties/new"
              className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
              style={{ backgroundColor: "#4A9B8E" }}
            >
              Add Property
            </Link>
          </Card>
        )}
      </div>

      {/* Upcoming Inspections */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Upcoming Inspections</h2>
          <Link href="/app/inspections" className="text-sm text-[#4A9B8E] hover:underline">
            View all →
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-16 rounded-xl" />
            <Skeleton className="h-16 rounded-xl" />
          </div>
        ) : dashboard && dashboard.upcoming_inspections.length > 0 ? (
          <div className="space-y-3">
            {dashboard.upcoming_inspections.map((insp) => (
              <Card key={insp.id} className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">{insp.property_address}</p>
                  <p className="text-xs text-muted-foreground">{insp.property_suburb}</p>
                </div>
                <p className="text-sm text-muted-foreground text-right shrink-0 ml-4">
                  {formatDateTime(insp.scheduled_at)}
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground text-sm mb-3">No inspections scheduled.</p>
            <Link
              href="/app/inspections"
              className="text-sm text-[#4A9B8E] hover:underline"
            >
              Schedule your first inspection
            </Link>
          </Card>
        )}
      </div>
    </div>
  );
}
