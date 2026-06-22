"use client";

import { useEffect, useState } from "react";
import { ScoreRing } from "./ScoreRing";

interface FamilyFitScoreProps {
  score: number | null;
  size?: "sm" | "lg";
  animate?: boolean;
}

export function FamilyFitScore({
  score,
  size = "lg",
  animate = false,
}: FamilyFitScoreProps) {
  const [displayScore, setDisplayScore] = useState<number | null>(
    animate ? 0 : score
  );

  useEffect(() => {
    if (!animate || score === null) {
      setDisplayScore(score);
      return;
    }
    setDisplayScore(0);
    const duration = 1200;
    const steps = 60;
    const stepDuration = duration / steps;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      setDisplayScore(parseFloat((score * progress).toFixed(1)));
      if (currentStep >= steps) {
        clearInterval(timer);
        setDisplayScore(score);
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [score, animate]);

  if (size === "sm") {
    return <ScoreRing score={displayScore} size={44} strokeWidth={4} />;
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <ScoreRing score={displayScore} size={80} strokeWidth={6} />
      <span className="text-lg font-medium text-muted-foreground">Family Fit</span>
    </div>
  );
}
