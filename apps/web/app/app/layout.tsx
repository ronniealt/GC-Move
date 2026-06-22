"use client";

import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import ErrorBoundary from "@/components/ErrorBoundary";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/app/dashboard", label: "Dashboard" },
  { href: "/app/properties", label: "Properties" },
  { href: "/app/shortlist", label: "Shortlist" },
  { href: "/app/suburbs", label: "Suburbs" },
  { href: "/app/schools", label: "Schools" },
  { href: "/app/advisor", label: "AI Advisor" },
  { href: "/app/journal", label: "Journal" },
  { href: "/app/inspections", label: "Inspections" },
  { href: "/app/preferences", label: "Preferences" },
  { href: "/app/settings", label: "Settings" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 border-r bg-background flex flex-col">
        <div className="px-4 py-5 border-b">
          <span className="font-semibold text-sm tracking-tight">GC Move OS</span>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-0.5">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "block px-3 py-2 rounded-md text-sm transition-colors",
                isActive(link.href)
                  ? "text-[#1A3C5E] bg-[#E8DCC8] border-l-[3px] border-[#4A9B8E] pl-[9px] font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="px-4 py-4 border-t">
          <UserButton />
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
    </div>
  );
}
