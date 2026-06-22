import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import PostHogInit from "@/components/PostHogInit";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "GC Move OS",
  description: "AI-powered Family Decision Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className={inter.variable}>
        <body className="antialiased">
          <PostHogInit />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
