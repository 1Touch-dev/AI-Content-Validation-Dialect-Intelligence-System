"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import ThreeDashboardBg from "@/components/three-dashboard-bg";
import SignOutButton from "@/components/signout-button";
import { backendFetch, clearAuthSession, getUsername } from "@/lib/backend-auth";
import {
  AudioLines,
  ClipboardCheck,
  Home,
  Image as ImageIcon,
  Sparkles,
  Video,
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    let active = true;
    async function verify() {
      const localUser = getUsername();
      setUsername(localUser || "User");
      try {
        const res = await backendFetch("/auth/me");
        if (!res.ok) {
          clearAuthSession();
          router.replace("/login");
          return;
        }
        const body = await res.json();
        if (active) {
          setUsername(body?.user?.username || localUser || "User");
          setReady(true);
        }
      } catch {
        clearAuthSession();
        router.replace("/login");
      }
    }
    verify();
    return () => {
      active = false;
    };
  }, [router]);

  if (!ready) {
    return (
      <main className="min-h-screen bg-[#060812] p-6 text-white">
        <div className="mx-auto max-w-5xl rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">
          Checking session...
        </div>
      </main>
    );
  }

  const navClass = (href: string) =>
    `flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition ${
      pathname === href
        ? "border-indigo-300/70 bg-indigo-300/20 text-white"
        : "border-white/15 bg-white/5 text-white/80 hover:bg-white/10 hover:text-white"
    }`;

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#060812] px-6 py-8 text-white lg:px-10">
      <ThreeDashboardBg />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,rgba(93,123,255,0.26),transparent_35%),radial-gradient(circle_at_80%_85%,rgba(197,78,255,0.2),transparent_45%)]" />

      <div className="relative z-10 mx-auto grid w-full max-w-[1600px] gap-8 lg:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="rounded-2xl border border-white/15 bg-[#0f1432]/85 p-5 backdrop-blur-xl">
          <p className="mb-1 text-xs uppercase tracking-[0.2em] text-white/60">
            Admin Console
          </p>
          <h1 className="flex items-center gap-2 text-lg font-semibold">
            <Sparkles className="h-4 w-4 text-indigo-200" />
            Dialect Intelligence
          </h1>
          <p className="mt-1 text-sm text-white/70">Signed in as {username}</p>

          <nav className="mt-7 space-y-2.5">
            <Link href="/dashboard" className={navClass("/dashboard")}>
              <Home className="h-4 w-4" />
              <span>Overview</span>
            </Link>
            <Link href="/dashboard/text" className={navClass("/dashboard/text")}>
              <ClipboardCheck className="h-4 w-4" />
              <span>Text Validator</span>
            </Link>
            <Link href="/dashboard/image" className={navClass("/dashboard/image")}>
              <ImageIcon className="h-4 w-4" />
              <span>Image Validator</span>
            </Link>
            <Link href="/dashboard/audio" className={navClass("/dashboard/audio")}>
              <AudioLines className="h-4 w-4" />
              <span>Audio Validator</span>
            </Link>
            <Link href="/dashboard/video" className={navClass("/dashboard/video")}>
              <Video className="h-4 w-4" />
              <span>Video Validator</span>
            </Link>
          </nav>

          <div className="mt-7 border-t border-white/10 pt-5">
            <SignOutButton />
          </div>
        </aside>

        <section className="space-y-6">
          <header className="rounded-2xl border border-white/15 bg-white/10 p-6 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-white/60">
                  Monitoring Workspace
                </p>
                <h2 className="mt-1 text-2xl font-semibold">Validation Admin Panel</h2>
                <p className="mt-1 text-sm text-white/70">
                  Manage all validation flows from one professional control center.
                </p>
              </div>
              <div className="hidden rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-right text-sm text-white/75 md:block">
                <p>Environment</p>
                <p className="font-medium text-white">Local Development</p>
              </div>
            </div>
          </header>

          <div className="rounded-2xl border border-white/15 bg-white/10 p-6 backdrop-blur-xl">
            {children}
          </div>
        </section>
      </div>
    </main>
  );
}
