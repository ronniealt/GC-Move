"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getMyFamily,
  updateFamily,
  getTargetSuburbs,
  setTargetSuburbs,
  getNonNegotiables,
  setNonNegotiables,
} from "@/lib/api/families";
import { listSuburbs } from "@/lib/api/suburbs";
import { NON_NEGOTIABLE_OPTIONS, MAX_TARGET_SUBURBS, PROPERTY_TYPE_OPTIONS } from "@/lib/constants";
import type { FamilyResponse, SuburbListItem } from "@/lib/types";

export default function PreferencesPage() {
  const { getToken, isLoaded } = useAuth();

  const [family, setFamily] = useState<FamilyResponse | null>(null);
  const [suburbs, setSuburbs] = useState<SuburbListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [budgetMin, setBudgetMin] = useState("");
  const [budgetMax, setBudgetMax] = useState("");
  const [savingBudget, setSavingBudget] = useState(false);

  const [selectedSuburbIds, setSelectedSuburbIds] = useState<string[]>([]);
  const [savingSuburbs, setSavingSuburbs] = useState(false);

  const [selectedNonNegotiables, setSelectedNonNegotiables] = useState<string[]>([]);
  const [propertyType, setPropertyType] = useState("any");
  const [savingNonNegotiables, setSavingNonNegotiables] = useState(false);

  useEffect(() => {
    document.title = "Preferences | GC Move OS";
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isLoaded) return;
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const [fam, suburbList] = await Promise.all([getMyFamily(token), listSuburbs(token)]);
        if (cancelled) return;
        setFamily(fam);
        setBudgetMin(fam.budget_min_aud?.toString() ?? "");
        setBudgetMax(fam.budget_max_aud?.toString() ?? "");
        setSuburbs(suburbList);

        const [targets, nonNegs] = await Promise.all([
          getTargetSuburbs(fam.id, token),
          getNonNegotiables(fam.id, token),
        ]);
        if (cancelled) return;
        setSelectedSuburbIds(targets.suburb_ids);
        setSelectedNonNegotiables(
          nonNegs
            .filter((n) => n.criterion_key !== "property_type")
            .map((n) => n.label)
            .filter((l): l is string => !!l)
        );
        const propertyTypeRow = nonNegs.find((n) => n.criterion_key === "property_type");
        setPropertyType(propertyTypeRow?.value ?? "any");
      } catch {
        toast.error("Failed to load preferences.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  async function handleSaveBudget() {
    if (!family) return;
    setSavingBudget(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const updated = await updateFamily(
        family.id,
        {
          budget_min_aud: budgetMin ? parseInt(budgetMin) : undefined,
          budget_max_aud: budgetMax ? parseInt(budgetMax) : undefined,
        },
        token
      );
      setFamily(updated);
      toast.success("Budget updated.");
    } catch {
      toast.error("Failed to update budget.");
    } finally {
      setSavingBudget(false);
    }
  }

  function toggleSuburb(id: string) {
    if (selectedSuburbIds.includes(id)) {
      setSelectedSuburbIds(selectedSuburbIds.filter((s) => s !== id));
    } else {
      if (selectedSuburbIds.length >= MAX_TARGET_SUBURBS) {
        toast.error(`You can pick up to ${MAX_TARGET_SUBURBS} suburbs`);
        return;
      }
      setSelectedSuburbIds([...selectedSuburbIds, id]);
    }
  }

  async function handleSaveSuburbs() {
    if (!family) return;
    setSavingSuburbs(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await setTargetSuburbs(family.id, selectedSuburbIds, token);
      toast.success("Target suburbs updated.");
    } catch {
      toast.error("Failed to update target suburbs.");
    } finally {
      setSavingSuburbs(false);
    }
  }

  function toggleNonNegotiable(item: string) {
    if (selectedNonNegotiables.includes(item)) {
      setSelectedNonNegotiables(selectedNonNegotiables.filter((n) => n !== item));
    } else {
      setSelectedNonNegotiables([...selectedNonNegotiables, item]);
    }
  }

  async function handleSaveNonNegotiables() {
    if (!family) return;
    setSavingNonNegotiables(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await setNonNegotiables(family.id, selectedNonNegotiables, token, propertyType);
      toast.success("Non-negotiables updated.");
    } catch {
      toast.error("Failed to update non-negotiables.");
    } finally {
      setSavingNonNegotiables(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8 max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Preferences</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Tell us exactly what matters — budget, suburbs, and must-haves.
        </p>
      </div>

      {/* Budget */}
      <Card className="p-5 space-y-4">
        <h2 className="text-base font-semibold">Budget</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="budget-min">Minimum (AUD)</Label>
            <Input
              id="budget-min"
              type="number"
              placeholder="e.g. 1000000"
              value={budgetMin}
              onChange={(e) => setBudgetMin(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="budget-max">Maximum (AUD)</Label>
            <Input
              id="budget-max"
              type="number"
              placeholder="e.g. 2000000"
              value={budgetMax}
              onChange={(e) => setBudgetMax(e.target.value)}
            />
          </div>
        </div>
        <Button
          onClick={handleSaveBudget}
          disabled={savingBudget}
          style={{ backgroundColor: "#4A9B8E" }}
          className="text-white"
        >
          {savingBudget ? "Saving..." : "Save Budget"}
        </Button>
      </Card>

      {/* Target Suburbs */}
      <Card className="p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Target Suburbs</h2>
          <span className="text-xs text-muted-foreground">
            {selectedSuburbIds.length} / {MAX_TARGET_SUBURBS} selected
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          Pick up to {MAX_TARGET_SUBURBS}. We&apos;ll watch these for new matching listings.
        </p>
        <div className="grid grid-cols-2 gap-2 max-h-72 overflow-y-auto">
          {suburbs.map((suburb) => (
            <label
              key={suburb.id}
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedSuburbIds.includes(suburb.id)}
                onChange={() => toggleSuburb(suburb.id)}
                className="h-4 w-4"
              />
              <span className="text-sm">
                {suburb.name} <span className="text-muted-foreground">({suburb.postcode})</span>
              </span>
            </label>
          ))}
        </div>
        <Button
          onClick={handleSaveSuburbs}
          disabled={savingSuburbs}
          style={{ backgroundColor: "#4A9B8E" }}
          className="text-white"
        >
          {savingSuburbs ? "Saving..." : "Save Suburbs"}
        </Button>
      </Card>

      {/* Non-Negotiables */}
      <Card className="p-5 space-y-4">
        <h2 className="text-base font-semibold">Must-Haves</h2>
        <p className="text-sm text-muted-foreground">
          Properties missing these will be flagged or filtered out.
        </p>

        <div className="space-y-2">
          <p className="text-sm font-medium">Property Type</p>
          <div className="grid grid-cols-1 gap-2">
            {PROPERTY_TYPE_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className="flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
              >
                <input
                  type="radio"
                  name="property-type"
                  checked={propertyType === opt.value}
                  onChange={() => setPropertyType(opt.value)}
                  className="h-4 w-4"
                />
                <span className="text-sm">{opt.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-2">
          {NON_NEGOTIABLE_OPTIONS.map((item) => (
            <label
              key={item}
              className="flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedNonNegotiables.includes(item)}
                onChange={() => toggleNonNegotiable(item)}
                className="h-4 w-4"
              />
              <span className="text-sm">{item}</span>
            </label>
          ))}
        </div>
        <Button
          onClick={handleSaveNonNegotiables}
          disabled={savingNonNegotiables}
          style={{ backgroundColor: "#4A9B8E" }}
          className="text-white"
        >
          {savingNonNegotiables ? "Saving..." : "Save Must-Haves"}
        </Button>
      </Card>
    </div>
  );
}
