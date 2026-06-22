"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { FamilyFitScore } from "@/components/score/FamilyFitScore";
import { CategoryScoreRow } from "@/components/score/CategoryScoreRow";
import { ScoreRing } from "@/components/score/ScoreRing";
import { RecommendationBadge } from "@/components/score/RecommendationBadge";
import { getProperty, updateProperty } from "@/lib/api/properties";
import { getEvaluation } from "@/lib/api/evaluations";
import { createInspection } from "@/lib/api/inspections";
import { ApiError } from "@/lib/api/client";
import { track } from "@/lib/analytics";
import type { PropertyResponse, EvaluationResponse } from "@/lib/types";

const formatAUD = (price: number | null) => {
  if (price === null) return "Price on request";
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 0,
  }).format(price);
};

export default function PropertyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const propertyId = params.id as string;

  const [property, setProperty] = useState<PropertyResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null);
  const [propertyLoading, setPropertyLoading] = useState(true);
  const [evalLoading, setEvalLoading] = useState(true);
  const [evalNotReady, setEvalNotReady] = useState(false);
  const [shortlisting, setShortlisting] = useState(false);

  const [inspectionDialogOpen, setInspectionDialogOpen] = useState(false);
  const [inspectionDate, setInspectionDate] = useState("");
  const [inspectionNotes, setInspectionNotes] = useState("");
  const [schedulingInspection, setSchedulingInspection] = useState(false);

  useEffect(() => {
    if (property) {
      document.title = `${property.address_street} | GC Move OS`;
    }
  }, [property]);

  useEffect(() => {
    let cancelled = false;
    async function loadProperty() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const prop = await getProperty(propertyId, token);
        if (!cancelled) {
          setProperty(prop);
          track("evaluation_viewed", { property_id: propertyId });
        }
      } catch {
        if (!cancelled) toast.error("Failed to load property.");
      } finally {
        if (!cancelled) setPropertyLoading(false);
      }
    }
    loadProperty();
    return () => { cancelled = true; };
  }, [propertyId, getToken]);

  useEffect(() => {
    let cancelled = false;
    async function loadEvaluation() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const ev = await getEvaluation(propertyId, token);
        if (!cancelled) setEvaluation(ev);
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError && err.status === 404) {
            setEvalNotReady(true);
          }
        }
      } finally {
        if (!cancelled) setEvalLoading(false);
      }
    }
    loadEvaluation();
    return () => { cancelled = true; };
  }, [propertyId, getToken]);

  const handleRefreshEval = () => {
    setEvalNotReady(false);
    setEvalLoading(true);
    getToken().then((token) => {
      if (!token) return;
      getEvaluation(propertyId, token)
        .then(setEvaluation)
        .catch((err) => {
          if (err instanceof ApiError && err.status === 404) {
            setEvalNotReady(true);
          }
        })
        .finally(() => setEvalLoading(false));
    });
  };

  const handleShortlist = async () => {
    setShortlisting(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const updated = await updateProperty(propertyId, { status: "shortlisted" }, token);
      setProperty(updated);
      track("property_shortlisted", { property_id: propertyId });
      toast.success("Saved to shortlist.");
    } catch {
      toast.error("Failed to update property.");
    } finally {
      setShortlisting(false);
    }
  };

  const handleScheduleInspection = async () => {
    if (!inspectionDate) {
      toast.error("Please select a date and time.");
      return;
    }
    setSchedulingInspection(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await createInspection(
        {
          property_id: propertyId,
          scheduled_at: new Date(inspectionDate).toISOString(),
          notes: inspectionNotes || undefined,
        },
        token
      );
      track("inspection_created", { property_id: propertyId });
      toast.success("Inspection scheduled.");
      setInspectionDialogOpen(false);
      setInspectionDate("");
      setInspectionNotes("");
    } catch {
      toast.error("Failed to schedule inspection.");
    } finally {
      setSchedulingInspection(false);
    }
  };

  if (propertyLoading) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-72 rounded-xl" />
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
      </div>
    );
  }

  if (!property) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <p className="text-muted-foreground">Property not found.</p>
        <Link href="/app/properties" className="text-sm underline mt-4 block">
          Back to Properties
        </Link>
      </div>
    );
  }

  const heroImage = property.images.find((img) => img.image_order === 0)?.image_url ?? null;

  const priceDisplay =
    property.price_is_range &&
    property.price_range_low_aud &&
    property.price_range_high_aud
      ? `${formatAUD(property.price_range_low_aud)} - ${formatAUD(property.price_range_high_aud)}`
      : formatAUD(property.listing_price_aud);

  const narratives = [
    { label: "Community", text: evaluation?.community_narrative },
    { label: "Lifestyle", text: evaluation?.lifestyle_narrative },
    { label: "Schools", text: evaluation?.school_narrative },
    { label: "Property", text: evaluation?.property_narrative },
    { label: "Financial", text: evaluation?.financial_narrative },
  ].filter((n) => n.text);

  return (
    <div className="pb-16">
      {/* Hero */}
      <div className="relative h-72 overflow-hidden">
        {heroImage ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={heroImage}
            alt={property.address_street}
            className="w-full h-full object-cover"
          />
        ) : (
          <div
            className="w-full h-full"
            style={{ background: "linear-gradient(135deg, #1A3C5E 0%, #4A9B8E 100%)" }}
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute bottom-4 left-6 text-white">
          <h1 className="text-2xl font-semibold">{property.address_street}</h1>
          <p className="text-white/80 text-sm">
            {property.address_suburb}, {property.address_state} {property.address_postcode}
          </p>
          <p className="text-lg font-bold mt-1">{priceDisplay}</p>
        </div>
        <div className="absolute top-4 right-4">
          <RecommendationBadge level={property.status} size="md" />
        </div>
      </div>

      <div className="p-6 max-w-4xl mx-auto space-y-6">
        {/* Family Fit Score */}
        <Card className="p-6 text-center">
          {evalLoading ? (
            <Skeleton className="h-32 w-32 rounded-full mx-auto" />
          ) : evalNotReady ? (
            <div className="space-y-3">
              <p className="text-muted-foreground text-sm">
                Evaluation is still being generated. Check back in a moment.
              </p>
              <Button variant="outline" size="sm" onClick={handleRefreshEval}>
                Refresh
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <FamilyFitScore
                score={evaluation?.scores?.family_fit_score ?? null}
                size="lg"
                animate={true}
              />
              {evaluation?.executive_summary && (
                <p className="text-muted-foreground text-sm max-w-xl mx-auto">
                  {evaluation.executive_summary}
                </p>
              )}
            </div>
          )}
        </Card>

        {/* Category Scores */}
        {!evalLoading && evaluation?.scores && (
          <Card className="p-6">
            <h2 className="text-base font-semibold mb-4">Dimension Scores</h2>
            <CategoryScoreRow scores={evaluation.scores} size="lg" />
          </Card>
        )}

        {/* Property Snapshot */}
        <Card className="p-6">
          <h2 className="text-base font-semibold mb-4">Property Snapshot</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              { label: "Bedrooms", value: property.bedrooms },
              { label: "Bathrooms", value: property.bathrooms },
              { label: "Car Spaces", value: property.car_spaces },
              {
                label: "Land Area",
                value: property.land_area_sqm ? `${property.land_area_sqm} m2` : null,
              },
              { label: "Type", value: property.property_type },
              { label: "Price", value: priceDisplay },
            ].map(({ label, value }) =>
              value !== null && value !== undefined ? (
                <div
                  key={label}
                  className="flex flex-col rounded-lg bg-muted/40 px-4 py-3"
                >
                  <span className="text-xs text-muted-foreground">{label}</span>
                  <span className="text-sm font-medium mt-0.5">{String(value)}</span>
                </div>
              ) : null
            )}
          </div>
        </Card>

        {/* Risk Flags */}
        {!evalLoading && evaluation && (
          <Card className="p-6">
            <h2 className="text-base font-semibold mb-4">Risk Assessment</h2>
            {evaluation.deal_breakers_flagged && evaluation.deal_breakers_flagged.length > 0 ? (
              <div className="space-y-2">
                {evaluation.deal_breakers_flagged.map((flag, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-200"
                  >
                    <svg
                      className="w-5 h-5 text-red-500 shrink-0 mt-0.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
                      />
                    </svg>
                    <p className="text-sm text-red-800">{flag}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-3 p-3 rounded-lg bg-green-50 border border-green-200">
                <svg
                  className="w-5 h-5 text-green-600 shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-sm text-green-800">No major risks identified.</p>
              </div>
            )}
          </Card>
        )}

        {/* Family Lens */}
        {!evalLoading && evaluation && evaluation.per_member.length > 0 && (
          <Card className="p-6">
            <h2 className="text-base font-semibold mb-4">Family Lens</h2>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {evaluation.per_member.map((member) => (
                <div
                  key={member.member_id}
                  className="w-60 shrink-0 rounded-xl border p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Member</span>
                    <ScoreRing score={member.fit_score} size={40} strokeWidth={4} />
                  </div>
                  <p className="text-sm leading-relaxed">{member.commentary}</p>
                  {member.key_positives && member.key_positives.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-green-700 mb-1">Positives</p>
                      <ul className="space-y-0.5">
                        {member.key_positives.map((p, i) => (
                          <li key={i} className="text-xs text-muted-foreground">
                            + {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {member.key_concerns && member.key_concerns.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-red-700 mb-1">Concerns</p>
                      <ul className="space-y-0.5">
                        {member.key_concerns.map((c, i) => (
                          <li key={i} className="text-xs text-muted-foreground">
                            - {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* AI Narratives */}
        {narratives.length > 0 && (
          <Card className="p-6">
            <h2 className="text-base font-semibold mb-4">AI Analysis</h2>
            <div className="space-y-2">
              {narratives.map(({ label, text }) => (
                <details key={label} className="group rounded-lg border overflow-hidden">
                  <summary className="flex items-center justify-between px-4 py-3 cursor-pointer select-none text-sm font-medium hover:bg-muted/40 transition-colors">
                    {label}
                    <svg
                      className="w-4 h-4 text-muted-foreground transition-transform group-open:rotate-180"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </summary>
                  <div className="px-4 pb-4 pt-2 text-sm text-muted-foreground leading-relaxed">
                    {text}
                  </div>
                </details>
              ))}
            </div>
          </Card>
        )}

        {/* Five Year Outlook */}
        {evaluation?.five_year_narrative && (
          <Card className="p-6">
            <h2 className="text-base font-semibold mb-3">Five Year Outlook</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {evaluation.five_year_narrative}
            </p>
          </Card>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
          <Link
            href="/app/properties"
            className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Properties
          </Link>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setInspectionDialogOpen(true)}
            >
              Book Inspection
            </Button>
            <Link href={`/app/advisor?property_id=${propertyId}`}>
              <Button variant="outline">Discuss with Advisor</Button>
            </Link>
            {property.status !== "shortlisted" && (
              <Button
                style={{ backgroundColor: "#4A9B8E" }}
                className="text-white"
                onClick={handleShortlist}
                disabled={shortlisting}
              >
                {shortlisting ? "Saving..." : "Save to Shortlist"}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Book Inspection Dialog */}
      <Dialog open={inspectionDialogOpen} onOpenChange={setInspectionDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Book Inspection</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {property && (
              <p className="text-sm text-muted-foreground">
                {property.address_street}, {property.address_suburb}
              </p>
            )}
            <div className="space-y-1.5">
              <Label>Date &amp; Time</Label>
              <Input
                type="datetime-local"
                value={inspectionDate}
                onChange={(e) => setInspectionDate(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Notes (optional)</Label>
              <Textarea
                placeholder="Agent name, open home details..."
                value={inspectionNotes}
                onChange={(e) => setInspectionNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setInspectionDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleScheduleInspection}
              disabled={schedulingInspection}
              style={{ backgroundColor: "#4A9B8E" }}
              className="text-white"
            >
              {schedulingInspection ? "Booking..." : "Book"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
