"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { ingestProperty, getProperty } from "@/lib/api/properties";
import { track } from "@/lib/analytics";

type PageState = "idle" | "submitting" | "polling" | "error";

const PROCESSING_STEPS = [
  "Fetching listing details",
  "Extracting property features",
  "Analysing location & suburb",
  "Evaluating school catchment",
  "Generating family report",
];

export default function NewPropertyPage() {
  const router = useRouter();
  const { getToken } = useAuth();

  const [url, setUrl] = useState("");
  const [pageState, setPageState] = useState<PageState>("idle");
  const [pollStep, setPollStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stepIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearAllTimers = useCallback(() => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    if (stepIntervalRef.current) clearInterval(stepIntervalRef.current);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    pollIntervalRef.current = null;
    stepIntervalRef.current = null;
    timeoutRef.current = null;
  }, []);

  const startPolling = useCallback(
    (propertyId: string) => {
      stepIntervalRef.current = setInterval(() => {
        setPollStep((prev) => Math.min(prev + 1, PROCESSING_STEPS.length - 1));
      }, 8000);

      pollIntervalRef.current = setInterval(async () => {
        try {
          const token = await getToken();
          if (!token) return;
          const prop = await getProperty(propertyId, token);
          if ((prop.status as string) !== "ingesting") {
            clearAllTimers();
            if ((prop.status as string) === "ingestion_failed") {
              setErrorMessage("The property could not be ingested. Please check the URL and try again.");
              setPageState("error");
            } else {
              router.push(`/app/properties/${propertyId}`);
            }
          }
        } catch {
          // continue polling on transient errors
        }
      }, 3000);

      timeoutRef.current = setTimeout(() => {
        clearAllTimers();
        setErrorMessage("This is taking longer than expected. Please try again.");
        setPageState("error");
      }, 90000);
    },
    [getToken, router, clearAllTimers]
  );

  const handleSubmit = async () => {
    const trimmedUrl = url.trim();
    if (!trimmedUrl.startsWith("http")) {
      toast.error("Please enter a valid URL.");
      return;
    }
    if (
      !trimmedUrl.includes("realestate.com.au") &&
      !trimmedUrl.includes("domain.com.au")
    ) {
      toast.error("URL must be from realestate.com.au or domain.com.au.");
      return;
    }

    setPageState("submitting");
    setPollStep(0);

    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const result = await ingestProperty({ url: trimmedUrl }, token);
      track("property_submitted", { url: trimmedUrl });
      setPageState("polling");
      startPolling(result.property_id);
    } catch {
      setErrorMessage("Failed to submit the property URL. Please try again.");
      setPageState("error");
    }
  };

  const handleReset = () => {
    clearAllTimers();
    setPollStep(0);
    setErrorMessage(null);
    setPageState("idle");
    setUrl("");
  };

  if (pageState === "polling") {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <h1 className="text-2xl font-semibold mb-2">Analysing property&hellip;</h1>
        <p className="text-muted-foreground text-sm mb-8">
          This usually takes 20&ndash;40 seconds. Please do not close this page.
        </p>

        <div className="space-y-4">
          {PROCESSING_STEPS.map((stepLabel, idx) => {
            const isComplete = idx < pollStep;
            const isActive = idx === pollStep;
            const isPending = idx > pollStep;

            return (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-8 h-8 flex items-center justify-center shrink-0">
                  {isComplete && (
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="#4A9B8E"
                      strokeWidth={2.5}
                    >
                      <circle cx="12" cy="12" r="10" strokeWidth="2" fill="rgba(74,155,142,0.1)" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8 12l3 3 5-5" />
                    </svg>
                  )}
                  {isActive && (
                    <svg
                      className="w-6 h-6 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="#4A9B8E"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        strokeWidth="3"
                        strokeDasharray="31.4"
                        strokeDashoffset="10"
                        opacity="0.3"
                      />
                      <path
                        d="M12 2a10 10 0 0 1 10 10"
                        strokeWidth="3"
                        strokeLinecap="round"
                      />
                    </svg>
                  )}
                  {isPending && (
                    <svg
                      className="w-6 h-6 text-gray-300"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <circle cx="12" cy="12" r="10" />
                    </svg>
                  )}
                </div>
                <span
                  className={`text-sm ${
                    isComplete
                      ? "text-muted-foreground line-through"
                      : isActive
                      ? "font-medium text-foreground"
                      : "text-muted-foreground"
                  }`}
                >
                  {stepLabel}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (pageState === "error") {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <h1 className="text-2xl font-semibold mb-2">Something went wrong</h1>
        <div className="mt-4 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
          {errorMessage ?? "An unexpected error occurred."}
        </div>
        <Button className="mt-6" onClick={handleReset} variant="outline">
          Try again
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-lg mx-auto">
      <h1 className="text-2xl font-semibold mb-1">Add a property</h1>
      <p className="text-muted-foreground text-sm mb-8">
        Paste a listing URL from realestate.com.au or domain.com.au and we will
        analyse it for your family.
      </p>

      <div className="space-y-4">
        <textarea
          className="w-full h-24 rounded-lg border border-input bg-background px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#4A9B8E]"
          placeholder="https://www.realestate.com.au/property/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={pageState === "submitting"}
        />
        <Button
          className="w-full text-white"
          style={{ backgroundColor: "#4A9B8E" }}
          onClick={handleSubmit}
          disabled={pageState === "submitting" || !url.trim()}
        >
          {pageState === "submitting" ? (
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
              Submitting...
            </span>
          ) : (
            "Analyse this property"
          )}
        </Button>
      </div>
    </div>
  );
}
