"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth, useUser } from "@clerk/nextjs";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useOnboardingStore } from "@/lib/stores/onboarding";
import {
  createFamily,
  addFamilyMember,
  setNonNegotiables,
  setTargetSuburbs,
  updateFamily,
} from "@/lib/api/families";
import { listSuburbs } from "@/lib/api/suburbs";
import type { SuburbListItem } from "@/lib/types";

const TOTAL_STEPS = 6;
const MAX_TARGET_SUBURBS = 5;

const ROLE_OPTIONS = [
  { value: "primary_adult", label: "Primary Adult" },
  { value: "secondary_adult", label: "Secondary Adult" },
  { value: "child", label: "Child" },
  { value: "pet", label: "Pet" },
];

const TIMELINE_OPTIONS = [
  "ASAP",
  "1-3 months",
  "3-6 months",
  "6-12 months",
  "Just exploring",
];

const NON_NEG_OPTIONS = [
  "4+ bedrooms",
  "Pool",
  "Double garage",
  "Somerset College catchment",
  "Under $2M",
  "Under $1.5M",
  "Beach < 10 min",
  "Home office",
];

export default function OnboardingPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { user } = useUser();
  const store = useOnboardingStore();
  const [submitting, setSubmitting] = useState(false);
  const [suburbs, setSuburbs] = useState<SuburbListItem[]>([]);

  const {
    step,
    familyName,
    members,
    budgetMin,
    budgetMax,
    moveTimeline,
    nonNegotiables,
    targetSuburbIds,
    setStep,
    setFamilyName,
    setMembers,
    setBudget,
    setMoveTimeline,
    setNonNegotiables: setNonNegotiablesLocal,
    setTargetSuburbIds,
  } = store;

  const currentMembers =
    members.length > 0 ? members : [{ name: "", role: "primary_adult", age: "" }];

  useEffect(() => {
    const token = getToken;
    (async () => {
      try {
        const t = await token();
        if (!t) return;
        setSuburbs(await listSuburbs(t));
      } catch {
        // Non-critical — the suburb-picker step just shows empty if this fails.
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleNext = () => {
    if (step === 2 && members.length === 0) {
      setMembers([{ name: "", role: "primary_adult", age: "" }]);
    }
    setStep(step + 1);
  };

  const handleBack = () => setStep(step - 1);

  const toggleNonNeg = (item: string) => {
    if (nonNegotiables.includes(item)) {
      setNonNegotiablesLocal(nonNegotiables.filter((n) => n !== item));
    } else {
      setNonNegotiablesLocal([...nonNegotiables, item]);
    }
  };

  const toggleSuburb = (id: string) => {
    if (targetSuburbIds.includes(id)) {
      setTargetSuburbIds(targetSuburbIds.filter((s) => s !== id));
    } else {
      if (targetSuburbIds.length >= MAX_TARGET_SUBURBS) {
        toast.error(`You can pick up to ${MAX_TARGET_SUBURBS} suburbs`);
        return;
      }
      setTargetSuburbIds([...targetSuburbIds, id]);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      const family = await createFamily(
        {
          display_name: familyName,
          user_display_name: user?.fullName ?? "User",
          user_email: user?.primaryEmailAddress?.emailAddress ?? "",
          budget_min_aud: budgetMin ? parseInt(budgetMin) : undefined,
          budget_max_aud: budgetMax ? parseInt(budgetMax) : undefined,
        },
        token
      );

      for (const member of currentMembers) {
        if (member.name.trim()) {
          await addFamilyMember(
            family.id,
            {
              first_name: member.name.trim(),
              role: member.role as "primary_adult" | "secondary_adult" | "child" | "pet",
              age: member.age ? parseInt(member.age) : undefined,
            },
            token
          );
        }
      }

      if (nonNegotiables.length > 0) {
        await setNonNegotiables(family.id, nonNegotiables, token);
      }

      if (targetSuburbIds.length > 0) {
        await setTargetSuburbs(family.id, targetSuburbIds, token);
      }

      await updateFamily(
        family.id,
        {
          onboarding_completed: true,
          ...(moveTimeline ? { target_move_timeline: moveTimeline } : {}),
        },
        token
      );

      store.reset();
      router.push("/app/dashboard?onboarding=complete");
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const progressPct = (step / TOTAL_STEPS) * 100;

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-lg">
        <div className="mb-8">
          <div className="flex justify-between text-xs text-muted-foreground mb-2">
            <span>Step {step} of {TOTAL_STEPS}</span>
            <span>{Math.round(progressPct)}%</span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{ width: `${progressPct}%`, backgroundColor: "#4A9B8E" }}
            />
          </div>
        </div>

        <div className="bg-card border rounded-xl p-8 shadow-sm">
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">Welcome to GC Move OS</h1>
                <p className="text-muted-foreground text-sm">
                  Let&apos;s set up your family profile in a few quick steps.
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="familyName">What do we call your family?</Label>
                <Input
                  id="familyName"
                  placeholder="e.g. The Smiths"
                  value={familyName}
                  onChange={(e) => setFamilyName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && familyName.trim() && handleNext()}
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">Who&apos;s in your family?</h1>
                <p className="text-muted-foreground text-sm">
                  Add each family member so we can personalise insights for everyone.
                </p>
              </div>
              <div className="space-y-3">
                {currentMembers.map((member, idx) => (
                  <div key={idx} className="flex gap-2 items-start">
                    <Input
                      placeholder="Name"
                      value={member.name}
                      className="flex-1"
                      onChange={(e) => {
                        const updated = [...currentMembers];
                        updated[idx] = { ...updated[idx], name: e.target.value };
                        setMembers(updated);
                      }}
                    />
                    <select
                      className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={member.role}
                      onChange={(e) => {
                        const updated = [...currentMembers];
                        updated[idx] = { ...updated[idx], role: e.target.value };
                        setMembers(updated);
                      }}
                    >
                      {ROLE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                    <Input
                      placeholder="Age"
                      type="number"
                      className="w-20"
                      value={member.age}
                      onChange={(e) => {
                        const updated = [...currentMembers];
                        updated[idx] = { ...updated[idx], age: e.target.value };
                        setMembers(updated);
                      }}
                    />
                    {currentMembers.length > 1 && (
                      <button
                        type="button"
                        className="text-muted-foreground hover:text-destructive text-lg leading-none mt-2"
                        onClick={() => {
                          setMembers(currentMembers.filter((_, i) => i !== idx));
                        }}
                      >
                        x
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setMembers([...currentMembers, { name: "", role: "child", age: "" }]);
                }}
              >
                + Add another member
              </Button>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">What&apos;s your budget?</h1>
                <p className="text-muted-foreground text-sm">
                  Used to calculate Financial Score. You can update this anytime.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="budgetMin">Minimum (AUD)</Label>
                  <Input
                    id="budgetMin"
                    type="number"
                    placeholder="e.g. 1000000"
                    value={budgetMin}
                    onChange={(e) => setBudget(e.target.value, budgetMax)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="budgetMax">Maximum (AUD)</Label>
                  <Input
                    id="budgetMax"
                    type="number"
                    placeholder="e.g. 2000000"
                    value={budgetMax}
                    onChange={(e) => setBudget(budgetMin, e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">When are you looking to move?</h1>
                <p className="text-muted-foreground text-sm">
                  Helps us prioritise urgency in your recommendations.
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {TIMELINE_OPTIONS.map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-colors ${
                      moveTimeline === option
                        ? "border-[#4A9B8E] font-medium"
                        : "border-input hover:bg-accent"
                    }`}
                    style={
                      moveTimeline === option
                        ? { backgroundColor: "rgba(74,155,142,0.08)" }
                        : undefined
                    }
                    onClick={() => setMoveTimeline(option)}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">Any must-haves?</h1>
                <p className="text-muted-foreground text-sm">
                  Select everything that applies. Properties missing these will be flagged.
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {NON_NEG_OPTIONS.map((item) => (
                  <label
                    key={item}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={nonNegotiables.includes(item)}
                      onChange={() => toggleNonNeg(item)}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">{item}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {step === 6 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-semibold mb-1">Which suburbs interest you?</h1>
                <p className="text-muted-foreground text-sm">
                  Pick up to {MAX_TARGET_SUBURBS}. We&apos;ll watch these for new matching listings.
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2 max-h-80 overflow-y-auto">
                {suburbs.map((suburb) => (
                  <label
                    key={suburb.id}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={targetSuburbIds.includes(suburb.id)}
                      onChange={() => toggleSuburb(suburb.id)}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">
                      {suburb.name} <span className="text-muted-foreground">({suburb.postcode})</span>
                    </span>
                  </label>
                ))}
                {suburbs.length === 0 && (
                  <p className="text-sm text-muted-foreground">Loading suburbs...</p>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mt-8">
            {step > 1 ? (
              <Button variant="outline" onClick={handleBack} disabled={submitting}>
                Back
              </Button>
            ) : (
              <div />
            )}

            <div className="flex items-center gap-3">
              {step === 3 && (
                <button
                  type="button"
                  className="text-sm text-muted-foreground hover:text-foreground"
                  onClick={handleNext}
                >
                  Skip for now
                </button>
              )}
              {step < TOTAL_STEPS ? (
                <Button
                  onClick={handleNext}
                  disabled={step === 1 && !familyName.trim()}
                  style={{ backgroundColor: "#4A9B8E" }}
                  className="text-white"
                >
                  Next
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={submitting}
                  style={{ backgroundColor: "#4A9B8E" }}
                  className="text-white"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8v8H4z"
                        />
                      </svg>
                      Setting up...
                    </span>
                  ) : (
                    "Get started"
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
