"use client";

import { ScoreRing } from "./ScoreRing";
import type { EvaluationScoresResponse } from "@/lib/types";

interface CategoryScoreRowProps {
  scores: EvaluationScoresResponse | null;
  size?: "sm" | "lg";
}

const CATEGORIES = [
  { label: "Community", key: "community_score" as keyof EvaluationScoresResponse },
  { label: "Lifestyle", key: "lifestyle_score" as keyof EvaluationScoresResponse },
  { label: "Schools", key: "school_score" as keyof EvaluationScoresResponse },
  { label: "Property", key: "property_score" as keyof EvaluationScoresResponse },
  { label: "Financial", key: "financial_score" as keyof EvaluationScoresResponse },
];

export function CategoryScoreRow({ scores, size = "lg" }: CategoryScoreRowProps) {
  const ringSize = size === "sm" ? 36 : 52;
  const labelClass = size === "sm" ? "text-xs" : "text-sm";

  return (
    <div className="flex items-center justify-around gap-2">
      {CATEGORIES.map(({ label, key }) => {
        const score = scores ? (scores[key] as number | null) : null;
        return (
          <div key={key} className="flex flex-col items-center gap-1">
            <ScoreRing score={score} size={ringSize} strokeWidth={4} />
            <span className={`${labelClass} text-muted-foreground text-center leading-tight`}>
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
