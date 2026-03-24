"use client";

import { useRouter } from "next/navigation";
import { backendFetch, clearAuthSession } from "@/lib/backend-auth";

export default function SignOutButton() {
  const router = useRouter();

  async function handleSignOut() {
    try {
      await backendFetch("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors during logout.
    } finally {
      clearAuthSession();
      router.push("/login");
    }
  }

  return (
    <button
      type="button"
      onClick={handleSignOut}
      className="w-full rounded-xl border border-white/20 bg-white/5 px-3 py-2 text-sm font-medium text-white transition hover:bg-white/10"
    >
      Sign out
    </button>
  );
}
