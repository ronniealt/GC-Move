"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { ArrowLeft, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getJournalEntry, deleteJournalEntry } from "@/lib/api/journal";
import type { JournalEntryResponse } from "@/lib/types";

const ENTRY_TYPE_LABELS: Record<string, string> = {
  note: "Note",
  reflection: "Reflection",
  decision: "Decision",
  question: "Question",
  milestone: "Milestone",
  concern: "Concern",
};

const MOOD_EMOJI: Record<string, string> = {
  excited: "🎉 Excited",
  positive: "😊 Positive",
  neutral: "😐 Neutral",
  uncertain: "🤔 Uncertain",
  concerned: "😟 Concerned",
};

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString("en-AU", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function JournalEntryPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const id = params.id as string;

  const [entry, setEntry] = useState<JournalEntryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await getJournalEntry(id, token);
        if (!cancelled) setEntry(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [id, getToken]);

  const handleDelete = async () => {
    const token = await getToken();
    if (!token || !entry) return;
    await deleteJournalEntry(entry.id, token);
    router.push("/app/journal");
  };

  if (loading) {
    return (
      <div className="p-8 max-w-3xl mx-auto space-y-4">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="p-8 max-w-3xl mx-auto">
        <p className="text-muted-foreground">Journal entry not found.</p>
        <button onClick={() => router.push("/app/journal")} className="mt-4 text-sm text-teal-600 hover:underline flex items-center gap-1">
          <ArrowLeft size={14} /> Back to Journal
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <button
        onClick={() => router.push("/app/journal")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        <ArrowLeft size={14} /> Journal
      </button>

      <Card>
        <CardContent className="pt-6 space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge>{ENTRY_TYPE_LABELS[entry.entry_type] ?? entry.entry_type}</Badge>
                {entry.mood && (
                  <span className="text-sm text-muted-foreground">{MOOD_EMOJI[entry.mood]}</span>
                )}
              </div>
              {entry.title && <h1 className="text-xl font-semibold">{entry.title}</h1>}
              <p className="text-xs text-muted-foreground">{formatDate(entry.created_at)}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="text-destructive hover:text-destructive shrink-0"
            >
              <Trash2 size={14} />
            </Button>
          </div>

          {/* Body */}
          <div className="prose prose-sm max-w-none">
            {entry.body.split("\n").map((line, i) => (
              <p key={i} className="text-sm leading-relaxed">{line}</p>
            ))}
          </div>

          {/* Tags */}
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex gap-1.5 flex-wrap pt-2">
              {entry.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
              ))}
            </div>
          )}

          {/* Linked property */}
          {entry.property && (
            <div
              className="mt-4 p-3 bg-muted rounded-lg cursor-pointer hover:bg-muted/80 transition-colors"
              onClick={() => router.push(`/app/properties/${entry.property!.id}`)}
            >
              <p className="text-xs text-muted-foreground mb-0.5">Linked property</p>
              <p className="text-sm font-medium">{entry.property.address_street}</p>
              <p className="text-xs text-muted-foreground">{entry.property.address_suburb}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
