"use client";

interface RecommendationBadgeProps {
  level: string | null | undefined;
  size?: "sm" | "md";
}

export function RecommendationBadge({
  level,
  size = "md",
}: RecommendationBadgeProps) {
  if (!level) return null;

  const padding = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";

  switch (level) {
    case "prioritise_immediately":
      return (
        <span
          className={`inline-flex items-center gap-1 rounded-full font-medium ${padding}`}
          style={{ backgroundColor: "rgba(74,155,142,0.1)", color: "#4A9B8E" }}
        >
          ⭐ Prioritise
        </span>
      );
    case "inspect":
      return (
        <span
          className={`inline-flex items-center gap-1 rounded-full font-medium bg-blue-100 text-blue-800 ${padding}`}
        >
          Inspect
        </span>
      );
    case "monitor":
      return (
        <span
          className={`inline-flex items-center gap-1 rounded-full font-medium bg-amber-100 text-amber-800 ${padding}`}
        >
          Monitor
        </span>
      );
    case "ignore":
      return (
        <span
          className={`inline-flex items-center gap-1 rounded-full font-medium bg-gray-100 text-gray-600 ${padding}`}
        >
          Pass
        </span>
      );
    default:
      return null;
  }
}
