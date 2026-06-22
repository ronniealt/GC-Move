"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { X, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { listPreferences, updatePreference, retirePreference } from "@/lib/api/preferences";
import type { PreferenceResponse } from "@/lib/types";

type ConfidenceLevel = "High" | "Medium" | "Inferred";

function confidenceLevel(confidence: number): ConfidenceLevel {
  if (confidence >= 0.75) return "High";
  if (confidence >= 0.4) return "Medium";
  return "Inferred";
}

const CONFIDENCE_COLORS: Record<ConfidenceLevel, string> = {
  High: "bg-green-100 text-green-700 border-green-200",
  Medium: "bg-amber-100 text-amber-700 border-amber-200",
  Inferred: "bg-slate-100 text-slate-500 border-slate-200",
};

interface PreferenceTagProps {
  pref: PreferenceResponse;
  onConfirm: (id: string) => void;
  onRetire: (id: string) => void;
}

function PreferenceTag({ pref, onConfirm, onRetire }: PreferenceTagProps) {
  const level = confidenceLevel(pref.confidence);
  const colorClass = CONFIDENCE_COLORS[level];

  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm ${colorClass}`}>
      {pref.is_deal_breaker && <span className="text-red-500 font-bold">!</span>}
      <span>{pref.attribute}</span>
      <span className="opacity-60 text-xs">{level}</span>
      {pref.status === "Emerging" && (
        <button
          onClick={() => onConfirm(pref.id)}
          className="ml-1 hover:opacity-80 transition-opacity"
          title="Confirm preference"
        >
          <Check size={12} />
        </button>
      )}
      <button
        onClick={() => onRetire(pref.id)}
        className="ml-0.5 hover:opacity-80 transition-opacity"
        title="Remove preference"
      >
        <X size={12} />
      </button>
    </div>
  );
}

export default function PreferencesPage() {
  const { getToken, isLoaded } = useAuth();
  const [preferences, setPreferences] = useState<PreferenceResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isLoaded) return;
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await listPreferences(token);
        if (!cancelled) setPreferences(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  const handleConfirm = async (id: string) => {
    const token = await getToken();
    if (!token) return;
    const updated = await updatePreference(id, { status: "Confirmed" }, token);
    setPreferences((prev) => prev.map((p) => (p.id === id ? updated : p)));
  };

  const handleRetire = async (id: string) => {
    const token = await getToken();
    if (!token) return;
    await retirePreference(id, token);
    setPreferences((prev) => prev.filter((p) => p.id !== id));
  };

  const byStatus = {
    dealBreakers: preferences.filter((p) => p.is_deal_breaker),
    confirmed: preferences.filter((p) => p.status === "Confirmed" && !p.is_deal_breaker),
    emerging: preferences.filter((p) => p.status === "Emerging"),
    negative: preferences.filter((p) =>
      p.negative_signal_count > p.positive_signal_count
    ),
  };

  const byCategory = preferences
    .filter((p) => !p.is_deal_breaker && p.status !== "Contradicted")
    .reduce<Record<string, PreferenceResponse[]>>((acc, p) => {
      acc[p.category] = acc[p.category] ?? [];
      acc[p.category].push(p);
      return acc;
    }, {});

  const isEmpty = preferences.length === 0;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Preference Profile</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          What your AI advisor has learned about your family
        </p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>
      ) : isEmpty ? (
        <Card>
          <CardContent className="py-12 text-center space-y-2">
            <p className="text-muted-foreground">
              Your preference profile is just getting started.
            </p>
            <p className="text-sm text-muted-foreground">
              As you evaluate properties and chat with your advisor, we&apos;ll build a detailed picture of what matters to your family.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Non-negotiables */}
          {byStatus.dealBreakers.length > 0 && (
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-base text-red-600">Non-Negotiables</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                {byStatus.dealBreakers.map((p) => (
                  <PreferenceTag key={p.id} pref={p} onConfirm={handleConfirm} onRetire={handleRetire} />
                ))}
              </CardContent>
            </Card>
          )}

          {/* Confirmed */}
          {byStatus.confirmed.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Confirmed Preferences</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                {byStatus.confirmed.map((p) => (
                  <PreferenceTag key={p.id} pref={p} onConfirm={handleConfirm} onRetire={handleRetire} />
                ))}
              </CardContent>
            </Card>
          )}

          {/* Emerging */}
          {byStatus.emerging.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Emerging Preferences</CardTitle>
                  <span className="text-xs text-muted-foreground">Tick to confirm · X to dismiss</span>
                </div>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                {byStatus.emerging.map((p) => (
                  <PreferenceTag key={p.id} pref={p} onConfirm={handleConfirm} onRetire={handleRetire} />
                ))}
              </CardContent>
            </Card>
          )}

          {/* By category */}
          {Object.entries(byCategory).map(([category, prefs]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-base capitalize">{category.replace(/_/g, " ")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {prefs.map((p) => (
                    <PreferenceTag key={p.id} pref={p} onConfirm={handleConfirm} onRetire={handleRetire} />
                  ))}
                </div>
                {/* Weight bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Weight</span>
                    <span>{(prefs.reduce((a, p) => a + p.current_weight, 0) / prefs.length).toFixed(1)} / 5</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-teal-500 rounded-full"
                      style={{ width: `${(prefs.reduce((a, p) => a + p.current_weight, 0) / prefs.length / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </>
      )}
    </div>
  );
}
