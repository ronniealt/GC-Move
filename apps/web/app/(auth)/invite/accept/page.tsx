"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function AcceptInviteContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  // TODO Task 0.4: validate token via GET /api/invite/validate?token=
  // then call POST /api/invite/accept after Clerk sign-up completes
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-2xl font-semibold mb-2">You've been invited</h1>
        {token ? (
          <p className="text-muted-foreground">Validating your invite...</p>
        ) : (
          <p className="text-destructive">Invalid invite link.</p>
        )}
      </div>
    </div>
  );
}

export default function AcceptInvitePage() {
  return (
    <Suspense>
      <AcceptInviteContent />
    </Suspense>
  );
}
