"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Pin, Trash2, Plus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { listJournalEntries, createJournalEntry, deleteJournalEntry } from "@/lib/api/journal";
import { track } from "@/lib/analytics";
import type { JournalEntryResponse } from "@/lib/types";

const ENTRY_TYPE_LABELS: Record<string, string> = {
  note: "Note",
  reflection: "Reflection",
  decision: "Decision",
  question: "Question",
  milestone: "Milestone",
  concern: "Concern",
};

const ENTRY_TYPE_COLORS: Record<string, string> = {
  note: "secondary",
  reflection: "default",
  decision: "default",
  question: "outline",
  milestone: "default",
  concern: "destructive",
};

const MOOD_EMOJI: Record<string, string> = {
  excited: "🎉",
  positive: "😊",
  neutral: "😐",
  uncertain: "🤔",
  concerned: "😟",
};

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

interface NewEntryFormProps {
  onSave: (entry: { title?: string; body: string; entry_type: string }) => void;
  onCancel: () => void;
  saving: boolean;
}

function NewEntryForm({ onSave, onCancel, saving }: NewEntryFormProps) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [entryType, setEntryType] = useState("note");

  return (
    <Card className="border-teal-300">
      <CardContent className="pt-4 space-y-3">
        <Input
          placeholder="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Textarea
          placeholder="What's on your mind?"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={4}
          autoFocus
        />
        <div className="flex items-center gap-2 flex-wrap">
          {Object.entries(ENTRY_TYPE_LABELS).map(([type, label]) => (
            <button
              key={type}
              onClick={() => setEntryType(type)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                entryType === type
                  ? "bg-teal-500 text-white border-teal-500"
                  : "border-border text-muted-foreground hover:text-foreground"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 justify-end">
          <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
          <Button
            size="sm"
            disabled={!body.trim() || saving}
            onClick={() => onSave({ title: title || undefined, body, entry_type: entryType })}
          >
            {saving ? "Saving…" : "Save Entry"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function JournalPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [entries, setEntries] = useState<JournalEntryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isLoaded) return;
      const token = await getToken();
      if (!token || cancelled) return;
      try {
        const data = await listJournalEntries(token);
        if (!cancelled) setEntries(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  const handleCreate = async (data: { title?: string; body: string; entry_type: string }) => {
    const token = await getToken();
    if (!token) return;
    setSaving(true);
    try {
      const newEntry = await createJournalEntry(data, token);
      setEntries((prev) => [newEntry, ...prev]);
      track("journal_entry_created", { entry_type: data.entry_type });
      setShowForm(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    const token = await getToken();
    if (!token) return;
    await deleteJournalEntry(id, token);
    setEntries((prev) => prev.filter((e) => e.id !== id));
  };

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Decision Journal</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Your moving journey, in your own words
          </p>
        </div>
        {!showForm && (
          <Button onClick={() => setShowForm(true)} size="sm" className="flex items-center gap-1.5">
            <Plus size={14} /> New Entry
          </Button>
        )}
      </div>

      {showForm && (
        <NewEntryForm
          onSave={handleCreate}
          onCancel={() => setShowForm(false)}
          saving={saving}
        />
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-lg" />
          ))}
        </div>
      ) : entries.length === 0 && !showForm ? (
        <Card>
          <CardContent className="py-12 text-center space-y-3">
            <p className="text-muted-foreground">Your decision journal is empty.</p>
            <p className="text-sm text-muted-foreground">
              Capture thoughts, decisions, and milestones as you explore properties.
            </p>
            <Button onClick={() => setShowForm(true)} variant="outline" size="sm">
              Write your first entry
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => (
            <Card
              key={entry.id}
              className={`cursor-pointer hover:shadow-md transition-shadow ${
                entry.is_pinned ? "border-amber-300" : ""
              }`}
              onClick={() => router.push(`/app/journal/${entry.id}`)}
            >
              <CardContent className="py-4 space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    {entry.is_pinned && <Pin size={12} className="text-amber-500 shrink-0" />}
                    <Badge variant={(ENTRY_TYPE_COLORS[entry.entry_type] ?? "secondary") as "secondary" | "default" | "outline" | "destructive"}>
                      {ENTRY_TYPE_LABELS[entry.entry_type] ?? entry.entry_type}
                    </Badge>
                    {entry.mood && (
                      <span className="text-sm">{MOOD_EMOJI[entry.mood] ?? ""}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs text-muted-foreground">{formatDate(entry.created_at)}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(entry.id); }}
                      className="text-muted-foreground hover:text-destructive transition-colors"
                      title="Delete entry"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>

                {entry.title && (
                  <p className="font-medium text-sm">{entry.title}</p>
                )}
                <p className="text-sm text-muted-foreground line-clamp-2">{entry.body}</p>

                {entry.property && (
                  <div className="text-xs text-teal-600 flex items-center gap-1">
                    <span>📍</span>
                    <span>{entry.property.address_street}, {entry.property.address_suburb}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
