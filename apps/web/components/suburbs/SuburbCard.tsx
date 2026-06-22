"use client";

import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/score/ScoreRing";
import type { SuburbListItem } from "@/lib/types";

interface SuburbCardProps {
  suburb: SuburbListItem;
}

const TIER_VARIANTS: Record<string, "default" | "secondary" | "outline"> = {
  Premium: "default",
  Good: "secondary",
  Acceptable: "outline",
};

export function SuburbCard({ suburb }: SuburbCardProps) {
  const tierVariant = TIER_VARIANTS[suburb.tier_label] ?? "outline";
  const combinedScore =
    suburb.community_score !== null && suburb.lifestyle_score !== null
      ? parseFloat(((suburb.community_score + suburb.lifestyle_score) / 2).toFixed(1))
      : suburb.community_score ?? suburb.lifestyle_score ?? null;

  return (
    <Link href={`/app/suburbs/${suburb.slug}`}>
      <Card className="p-5 hover:shadow-md transition-shadow cursor-pointer h-full flex flex-col gap-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-semibold text-base">{suburb.name}</p>
            <p className="text-xs text-muted-foreground">{suburb.postcode}</p>
          </div>
          <Badge variant={tierVariant}>{suburb.tier_label}</Badge>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-center gap-1">
            <ScoreRing score={suburb.community_score} size={44} strokeWidth={4} />
            <span className="text-xs text-muted-foreground">Community</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <ScoreRing score={suburb.lifestyle_score} size={44} strokeWidth={4} />
            <span className="text-xs text-muted-foreground">Lifestyle</span>
          </div>
          {suburb.beach_access_minutes !== null && (
            <div className="ml-auto text-right">
              <p className="text-lg font-semibold">{suburb.beach_access_minutes}m</p>
              <p className="text-xs text-muted-foreground">to beach</p>
            </div>
          )}
        </div>
      </Card>
    </Link>
  );
}
