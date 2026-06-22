"use client";

interface ScoreRingProps {
  score: number | null;
  size?: number;
  strokeWidth?: number;
}

function scoreColor(score: number | null): string {
  if (score === null) return "#D1D5DB";
  if (score >= 7) return "#4A9B8E";
  if (score >= 5) return "#F59E0B";
  return "#EF4444";
}

export function ScoreRing({
  score,
  size = 48,
  strokeWidth = 4,
}: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const ratio = score !== null ? Math.max(0, Math.min(10, score)) / 10 : 0;
  const dashArray = `${circumference * ratio} ${circumference * (1 - ratio)}`;
  const color = scoreColor(score);
  const center = size / 2;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ display: "block" }}>
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="#E5E7EB"
        strokeWidth={strokeWidth}
      />
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={dashArray}
        strokeLinecap="round"
        transform={`rotate(-90 ${center} ${center})`}
      />
      <text
        x={center}
        y={center}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size * 0.28}
        fontWeight="600"
        fill={color}
      >
        {score !== null ? score.toFixed(1) : "—"}
      </text>
    </svg>
  );
}
