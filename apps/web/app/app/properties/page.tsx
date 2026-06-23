"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { listProperties } from "@/lib/api/properties";
import type { PropertyListResponse, PropertyStatus } from "@/lib/types";

const formatAUD = (price: number | null) => {
  if (price === null) return "POA";
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 0,
  }).format(price);
};

function statusBadge(status: string) {
  const base = "inline-flex px-2 py-0.5 rounded-full text-xs font-medium";
  switch (status) {
    case "ingesting":
      return <span className={`${base} bg-yellow-100 text-yellow-800`}>Ingesting</span>;
    case "shortlisted":
      return (
        <span className={`${base} text-white`} style={{ backgroundColor: "#4A9B8E" }}>
          Shortlisted
        </span>
      );
    case "saved":
      return (
        <span className={`${base} text-white`} style={{ backgroundColor: "#4A9B8E" }}>
          Saved
        </span>
      );
    case "rejected":
      return <span className={`${base} bg-gray-100 text-gray-600`}>Passed</span>;
    case "offer":
      return <span className={`${base} bg-green-100 text-green-800`}>Offer</span>;
    case "inspecting":
      return <span className={`${base} bg-blue-100 text-blue-800`}>Inspecting</span>;
    default:
      return <span className={`${base} bg-gray-100 text-gray-600`}>{status}</span>;
  }
}

export default function PropertiesPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();

  const [properties, setProperties] = useState<PropertyListResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    let cancelled = false;
    async function load() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const data = await listProperties(token);
        if (!cancelled) setProperties(data);
      } catch {
        // silently fail
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Your Properties</h1>
        <Link href="/app/properties/new">
          <Button style={{ backgroundColor: "#4A9B8E" }} className="text-white">
            Add Property
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      ) : properties.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-muted-foreground mb-4">
            No properties yet. Add your first one to get started.
          </p>
          <Link href="/app/properties/new">
            <Button style={{ backgroundColor: "#4A9B8E" }} className="text-white">
              Add Property
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {properties.map((prop) => (
            <Card
              key={prop.id}
              className="p-5 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(`/app/properties/${prop.id}`)}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-sm leading-tight">{prop.address_street}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {prop.address_suburb}, {prop.address_postcode}
                  </p>
                </div>
                {statusBadge(prop.status)}
              </div>

              <p className="text-base font-bold mt-3">
                {formatAUD(prop.listing_price_aud)}
              </p>

              <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                {prop.bedrooms !== null && (
                  <span>{prop.bedrooms} bed{prop.bedrooms !== 1 ? "s" : ""}</span>
                )}
                {prop.bathrooms !== null && (
                  <span>{prop.bathrooms} bath{prop.bathrooms !== 1 ? "s" : ""}</span>
                )}
                <span className="capitalize text-xs">{prop.property_type}</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
