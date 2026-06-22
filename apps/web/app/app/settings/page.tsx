"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { getMyFamily } from "@/lib/api/families";
import { apiCall } from "@/lib/api/client";
import type { FamilyResponse } from "@/lib/types";

const WEIGHT_LABELS: Record<string, string> = {
  weight_community: "Community",
  weight_lifestyle: "Lifestyle",
  weight_school: "Schools",
  weight_property: "Property",
  weight_financial: "Financial",
};

export default function SettingsPage() {
  const { getToken, isLoaded } = useAuth();
  const router = useRouter();

  const [family, setFamily] = useState<FamilyResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [displayName, setDisplayName] = useState("");
  const [savingName, setSavingName] = useState(false);

  const [inviteEmail, setInviteEmail] = useState("");
  const [sendingInvite, setSendingInvite] = useState(false);

  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  useEffect(() => {
    document.title = "Settings | GC Move OS";
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isLoaded) return;
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const fam = await getMyFamily(token);
        if (!cancelled) {
          setFamily(fam);
          setDisplayName(fam.display_name);
        }
      } catch {
        toast.error("Failed to load family settings.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  async function handleSaveName() {
    if (!family || !displayName.trim()) return;
    setSavingName(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const updated = await apiCall<FamilyResponse>(`/api/families/${family.id}`, {
        method: "PATCH",
        body: JSON.stringify({ display_name: displayName.trim() }),
        token,
      });
      setFamily(updated);
      toast.success("Family name updated.");
    } catch {
      toast.error("Failed to update family name.");
    } finally {
      setSavingName(false);
    }
  }

  async function handleSendInvite() {
    if (!family || !inviteEmail.trim()) return;
    setSendingInvite(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await apiCall(`/api/families/${family.id}/invite`, {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail.trim(), role: "member" }),
        token,
      });
      setInviteEmail("");
      toast.success("Invite sent!");
    } catch {
      toast.error("Failed to send invite. They may already have a pending invite.");
    } finally {
      setSendingInvite(false);
    }
  }

  function handleResetConfirm() {
    setResetDialogOpen(false);
    router.push("/onboarding");
  }

  if (loading) {
    return (
      <div className="p-8 max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Manage your family account and preferences.
        </p>
      </div>

      {/* Family Name */}
      <Card className="p-5 space-y-4">
        <h2 className="text-base font-semibold">Family Name</h2>
        <div className="flex items-end gap-3">
          <div className="flex-1 space-y-1.5">
            <Label htmlFor="display-name">Display name</Label>
            <Input
              id="display-name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Altit Family"
            />
          </div>
          <Button
            onClick={handleSaveName}
            disabled={savingName || displayName === family?.display_name}
            style={{ backgroundColor: "#4A9B8E" }}
            className="text-white"
          >
            {savingName ? "Saving..." : "Save"}
          </Button>
        </div>
      </Card>

      {/* Invite */}
      <Card className="p-5 space-y-4">
        <h2 className="text-base font-semibold">Invite a Family Member</h2>
        <p className="text-sm text-muted-foreground">
          They&apos;ll receive an email to join your family account and see the same
          properties, scores, and journal.
        </p>
        <div className="flex items-end gap-3">
          <div className="flex-1 space-y-1.5">
            <Label htmlFor="invite-email">Email address</Label>
            <Input
              id="invite-email"
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="partner@example.com"
              onKeyDown={(e) => e.key === "Enter" && handleSendInvite()}
            />
          </div>
          <Button
            onClick={handleSendInvite}
            disabled={sendingInvite || !inviteEmail.trim()}
            variant="outline"
          >
            {sendingInvite ? "Sending..." : "Send Invite"}
          </Button>
        </div>
      </Card>

      {/* Scoring Weights */}
      <Card className="p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Scoring Weights</h2>
          <Link
            href="/app/preferences"
            className="text-sm text-[#4A9B8E] hover:underline"
          >
            Edit in Preferences →
          </Link>
        </div>
        {family && (
          <div className="grid grid-cols-5 gap-3">
            {Object.entries(WEIGHT_LABELS).map(([key, label]) => {
              const value = (family as unknown as Record<string, unknown>)[key] as number;
              return (
                <div key={key} className="text-center">
                  <p className="text-xl font-bold text-[#1A3C5E]">
                    {Math.round((value ?? 0) * 100)}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Danger Zone */}
      <Card className="p-5 space-y-4 border-red-200">
        <h2 className="text-base font-semibold text-red-600">Danger Zone</h2>
        <Separator className="bg-red-100" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Reset onboarding</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Restart the setup flow. Your properties and evaluations won&apos;t be deleted.
            </p>
          </div>
          <Button
            variant="outline"
            className="border-red-300 text-red-600 hover:bg-red-50"
            onClick={() => setResetDialogOpen(true)}
          >
            Reset
          </Button>
        </div>
      </Card>

      {/* Reset confirmation dialog */}
      <Dialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Reset onboarding?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground py-2">
            You&apos;ll be taken back to the onboarding flow. Your existing data won&apos;t
            be deleted. Continue?
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setResetDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              className="bg-red-600 text-white hover:bg-red-700"
              onClick={handleResetConfirm}
            >
              Reset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
