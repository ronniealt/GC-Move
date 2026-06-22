"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { listInspections, createInspection, updateInspection, deleteInspection } from "@/lib/api/inspections";
import { listProperties } from "@/lib/api/properties";
import { track } from "@/lib/analytics";
import type { InspectionResponse, PropertyListResponse } from "@/lib/types";

function formatDateTime(dt: string | null) {
  if (!dt) return "TBD";
  return new Date(dt).toLocaleString("en-AU", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function InspectionCard({
  inspection,
  onMarkAttended,
  onDelete,
  onReschedule,
}: {
  inspection: InspectionResponse;
  onMarkAttended: (id: string) => void;
  onDelete: (id: string) => void;
  onReschedule: (inspection: InspectionResponse) => void;
}) {
  return (
    <Card className="p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-sm">
            {inspection.property?.address_street ?? "Unknown property"}
          </p>
          <p className="text-xs text-muted-foreground">
            {inspection.property?.address_suburb ?? ""}
          </p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            inspection.status === "scheduled"
              ? "bg-teal-100 text-teal-700"
              : inspection.status === "completed"
              ? "bg-green-100 text-green-700"
              : "bg-muted text-muted-foreground"
          }`}
        >
          {inspection.status.charAt(0).toUpperCase() + inspection.status.slice(1)}
        </span>
      </div>

      <p className="text-sm text-muted-foreground">
        {formatDateTime(inspection.scheduled_at)}
      </p>

      {inspection.notes && (
        <p className="text-xs text-muted-foreground border-l-2 border-muted pl-2">
          {inspection.notes}
        </p>
      )}

      <div className="flex items-center gap-2 pt-1">
        {inspection.status === "scheduled" && (
          <>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onMarkAttended(inspection.id)}
            >
              Mark Attended
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onReschedule(inspection)}
            >
              Reschedule
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="ghost"
          className="text-destructive hover:text-destructive ml-auto"
          onClick={() => onDelete(inspection.id)}
        >
          Delete
        </Button>
      </div>
    </Card>
  );
}

export default function InspectionsPage() {
  const { getToken, isLoaded } = useAuth();

  const [inspections, setInspections] = useState<InspectionResponse[]>([]);
  const [properties, setProperties] = useState<PropertyListResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingInspection, setEditingInspection] = useState<InspectionResponse | null>(null);
  const [selectedPropertyId, setSelectedPropertyId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    document.title = "Inspections | GC Move OS";
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isLoaded) return;
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const [insp, props] = await Promise.all([
          listInspections(token),
          listProperties(token),
        ]);
        if (!cancelled) {
          setInspections(insp);
          setProperties(props);
        }
      } catch {
        toast.error("Failed to load inspections.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  const upcoming = inspections.filter((i) => i.status === "scheduled");
  const past = inspections.filter((i) => i.status !== "scheduled");

  function openCreateDialog() {
    setEditingInspection(null);
    setSelectedPropertyId("");
    setScheduledAt("");
    setNotes("");
    setDialogOpen(true);
  }

  function openRescheduleDialog(inspection: InspectionResponse) {
    setEditingInspection(inspection);
    setSelectedPropertyId(inspection.property_id);
    setScheduledAt(
      inspection.scheduled_at
        ? new Date(inspection.scheduled_at).toISOString().slice(0, 16)
        : ""
    );
    setNotes(inspection.notes ?? "");
    setDialogOpen(true);
  }

  async function handleSave() {
    if (!scheduledAt) {
      toast.error("Please select a date and time.");
      return;
    }
    if (!editingInspection && !selectedPropertyId) {
      toast.error("Please select a property.");
      return;
    }
    setSaving(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      if (editingInspection) {
        const updated = await updateInspection(
          editingInspection.id,
          { scheduled_at: new Date(scheduledAt).toISOString() },
          token
        );
        setInspections((prev) =>
          prev.map((i) => (i.id === updated.id ? updated : i))
        );
        toast.success("Inspection rescheduled.");
      } else {
        const created = await createInspection(
          {
            property_id: selectedPropertyId,
            scheduled_at: new Date(scheduledAt).toISOString(),
            notes: notes || undefined,
          },
          token
        );
        setInspections((prev) => [created, ...prev]);
        track("inspection_created", { property_id: selectedPropertyId });
        toast.success("Inspection scheduled.");
      }
      setDialogOpen(false);
    } catch {
      toast.error("Failed to save inspection.");
    } finally {
      setSaving(false);
    }
  }

  async function handleMarkAttended(id: string) {
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const updated = await updateInspection(id, { status: "completed" }, token);
      setInspections((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
      toast.success("Marked as attended.");
    } catch {
      toast.error("Failed to update inspection.");
    }
  }

  async function handleDelete(id: string) {
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await deleteInspection(id, token);
      setInspections((prev) => prev.filter((i) => i.id !== id));
      toast.success("Inspection deleted.");
    } catch {
      toast.error("Failed to delete inspection.");
    }
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Inspections</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Track your scheduled and completed property inspections.
          </p>
        </div>
        <Button
          onClick={openCreateDialog}
          style={{ backgroundColor: "#4A9B8E" }}
          className="text-white"
        >
          Schedule Inspection
        </Button>
      </div>

      {/* Upcoming */}
      <section>
        <h2 className="text-base font-semibold mb-3">Upcoming</h2>
        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
          </div>
        ) : upcoming.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground text-sm">
              No inspections scheduled.{" "}
              <button
                className="underline"
                onClick={openCreateDialog}
              >
                Schedule one now.
              </button>
            </p>
          </Card>
        ) : (
          <div className="space-y-3">
            {upcoming.map((i) => (
              <InspectionCard
                key={i.id}
                inspection={i}
                onMarkAttended={handleMarkAttended}
                onDelete={handleDelete}
                onReschedule={openRescheduleDialog}
              />
            ))}
          </div>
        )}
      </section>

      {/* Past */}
      {past.length > 0 && (
        <section>
          <h2 className="text-base font-semibold mb-3 text-muted-foreground">Past</h2>
          <div className="space-y-3">
            {past.map((i) => (
              <InspectionCard
                key={i.id}
                inspection={i}
                onMarkAttended={handleMarkAttended}
                onDelete={handleDelete}
                onReschedule={openRescheduleDialog}
              />
            ))}
          </div>
        </section>
      )}

      {/* Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingInspection ? "Reschedule Inspection" : "Schedule Inspection"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {!editingInspection && (
              <div className="space-y-1.5">
                <Label>Property</Label>
                <Select
                  value={selectedPropertyId}
                  onValueChange={(v) => setSelectedPropertyId(v ?? "")}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a property" />
                  </SelectTrigger>
                  <SelectContent>
                    {properties.map((p) => (
                      <SelectItem key={p.id} value={p.id}>
                        {p.address_street}, {p.address_suburb}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {editingInspection && (
              <p className="text-sm text-muted-foreground">
                {editingInspection.property?.address_street},{" "}
                {editingInspection.property?.address_suburb}
              </p>
            )}

            <div className="space-y-1.5">
              <Label>Date &amp; Time</Label>
              <Input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </div>

            {!editingInspection && (
              <div className="space-y-1.5">
                <Label>Notes (optional)</Label>
                <Textarea
                  placeholder="Agent name, open home details, anything to remember..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
              style={{ backgroundColor: "#4A9B8E" }}
              className="text-white"
            >
              {saving ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
