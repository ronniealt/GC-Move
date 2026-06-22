"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/score/ScoreRing";
import type { SchoolListItem } from "@/lib/types";

interface SchoolCardProps {
  school: SchoolListItem;
  featured?: boolean;
}

const SECTOR_LABELS: Record<string, string> = {
  independent: "Independent",
  catholic: "Catholic",
  government: "Government",
};

const formatFee = (fee: number | null) => {
  if (fee === null) return null;
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 0,
  }).format(fee);
};

export function SchoolCard({ school, featured = false }: SchoolCardProps) {
  const score = school.metrics?.school_score ?? null;

  return (
    <Card className={featured ? "border-2 border-teal-500" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-base leading-tight truncate">{school.name}</p>
            <p className="text-sm text-muted-foreground mt-0.5">
              {school.address_suburb} · {school.year_range ?? "All years"}
            </p>
          </div>
          <div className="flex flex-col items-center gap-0.5 shrink-0">
            <ScoreRing score={score} size={48} strokeWidth={4} />
            <span className="text-xs text-muted-foreground">Score</span>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <Badge variant="outline">{SECTOR_LABELS[school.sector] ?? school.sector}</Badge>
          {featured && <Badge className="bg-teal-500 text-white hover:bg-teal-600">Featured</Badge>}
          {school.metrics?.has_boarding && <Badge variant="secondary">Boarding</Badge>}
        </div>
      </CardHeader>
      <CardContent className="pt-0 grid grid-cols-2 gap-3">
        {school.icsea !== null && (
          <div>
            <p className="text-xs text-muted-foreground">ICSEA</p>
            <p className="text-sm font-medium">{school.icsea}</p>
          </div>
        )}
        {school.total_enrolments !== null && (
          <div>
            <p className="text-xs text-muted-foreground">Enrolments</p>
            <p className="text-sm font-medium">{school.total_enrolments}</p>
          </div>
        )}
        {school.metrics?.annual_fee_aud !== null && school.metrics?.annual_fee_aud !== undefined && (
          <div>
            <p className="text-xs text-muted-foreground">Annual Fees</p>
            <p className="text-sm font-medium">{formatFee(school.metrics.annual_fee_aud)}</p>
          </div>
        )}
        {school.metrics?.academic_outcomes_score !== null && school.metrics?.academic_outcomes_score !== undefined && (
          <div>
            <p className="text-xs text-muted-foreground">Academic</p>
            <p className="text-sm font-medium">{school.metrics.academic_outcomes_score.toFixed(1)} / 10</p>
          </div>
        )}
        {school.website_url && (
          <div className="col-span-2 pt-1">
            <a
              href={school.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-teal-600 hover:underline"
              onClick={(e) => e.stopPropagation()}
            >
              Visit website →
            </a>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
