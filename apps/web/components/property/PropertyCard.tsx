"use client";

import { Card } from "@/components/ui/card";
import { FamilyFitScore } from "@/components/score/FamilyFitScore";
import { RecommendationBadge } from "@/components/score/RecommendationBadge";
import type { TopPropertyItem } from "@/lib/types";

interface PropertyCardProps {
  property: TopPropertyItem;
  onClick?: () => void;
}

const formatAUD = (price: number | null) => {
  if (price === null) return "Price on request";
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 0,
  }).format(price);
};

export function PropertyCard({ property, onClick }: PropertyCardProps) {
  return (
    <Card
      className="overflow-hidden cursor-pointer hover:shadow-md transition-shadow w-72 shrink-0"
      onClick={onClick}
    >
      {/* Image area */}
      <div className="relative aspect-video overflow-hidden">
        {property.hero_image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={property.hero_image_url}
            alt={property.address_street}
            className="w-full h-full object-cover"
          />
        ) : (
          <div
            className="w-full h-full"
            style={{ background: "linear-gradient(135deg, #1A3C5E 0%, #4A9B8E 100%)" }}
          />
        )}
        <div className="absolute top-2 right-2">
          <RecommendationBadge level={property.status} size="sm" />
        </div>
        {property.auto_discovered && !property.viewed_at && (
          <div className="absolute top-2 left-2">
            <span className="rounded-full bg-amber-500 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-white shadow-sm">
              New
            </span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="p-4 space-y-2">
        <div>
          <p className="font-semibold text-sm leading-tight">{property.address_street}</p>
          <p className="text-xs text-muted-foreground">
            {property.address_suburb}
          </p>
        </div>

        <p className="text-sm font-medium">{formatAUD(property.listing_price_aud)}</p>

        {/* Bottom row */}
        <div className="flex items-center justify-between pt-1">
          <FamilyFitScore score={property.family_fit_score} size="sm" />
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            {property.bedrooms !== null && (
              <span className="flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8" />
                  <path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4" />
                  <path d="M12 4v6" />
                  <path d="M2 18h20" />
                </svg>
                {property.bedrooms}
              </span>
            )}
            {property.bathrooms !== null && (
              <span className="flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5" />
                  <line x1="10" x2="8" y1="5" y2="7" />
                  <line x1="2" x2="22" y1="12" y2="12" />
                  <line x1="7" x2="7" y1="19" y2="21" />
                  <line x1="17" x2="17" y1="19" y2="21" />
                </svg>
                {property.bathrooms}
              </span>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
