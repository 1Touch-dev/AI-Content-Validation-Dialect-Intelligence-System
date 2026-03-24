"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import ThreeLandingBg from "@/components/three-landing-bg";
import { backendBaseUrl, setAuthSession } from "@/lib/backend-auth";

export default function LoginPage() {
  const router = useRouter();
  const callbackUrl = "/dashboard";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [regUsername, setRegUsername] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirm, setRegConfirm] = useState("");
  const [regLoading, setRegLoading] = useState(false);
  const [regMessage, setRegMessage] = useState("");
  const [regError, setRegError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${backendBaseUrl()}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body?.detail || "Invalid credentials.");
        return;
      }
      setAuthSession(body.access_token, body.username);
      router.push(callbackUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: FormEvent) {
    e.preventDefault();
    setRegError("");
    setRegMessage("");

    if (regPassword !== regConfirm) {
      setRegError("Passwords do not match.");
      return;
    }

    setRegLoading(true);
    try {
      const res = await fetch(`${backendBaseUrl()}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: regUsername,
          password: regPassword,
        }),
      });
      const body = await res.json();
      if (!res.ok) {
        setRegError(body?.detail || "Registration failed");
        return;
      }

      setRegMessage("Registration successful. You can sign in now.");
      setUsername(regUsername);
      setRegUsername("");
      setRegPassword("");
      setRegConfirm("");
    } catch (err) {
      setRegError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setRegLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#060812] text-white">
      <ThreeLandingBg />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_20%,rgba(93,123,255,0.28),transparent_35%),radial-gradient(circle_at_80%_70%,rgba(197,78,255,0.2),transparent_45%)]" />

      <section className="relative z-10 flex min-h-screen items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="w-full max-w-md rounded-2xl border border-white/20 bg-white/10 p-6 shadow-2xl backdrop-blur-xl"
        >
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-white/70">
            Secure Access
          </p>
          <h1 className="mb-2 text-2xl font-semibold">Sign in</h1>
          <p className="mb-6 text-sm text-white/75">
            Access the AI validation dashboard.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-white/90">Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/50 outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
                placeholder="Enter username"
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-white/90">Password</label>
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/50 outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
                placeholder="Enter password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-white px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-white/90 disabled:opacity-60"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>

            <button
              type="button"
              onClick={() => {
                setShowRegister(true);
                setRegError("");
                setRegMessage("");
              }}
              className="w-full rounded-md border border-white/30 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              Create account
            </button>
          </form>

          {error ? (
            <p className="mt-4 rounded-md border border-red-300/45 bg-red-500/15 p-2 text-sm text-red-100">
              {error}
            </p>
          ) : null}
        </motion.div>

        {showRegister ? (
          <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-6">
            <motion.div
              initial={{ opacity: 0, y: 18, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25 }}
              className="w-full max-w-md rounded-2xl border border-white/20 bg-[#101633]/90 p-6 shadow-2xl backdrop-blur-xl"
            >
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold">Register account</h2>
                <button
                  type="button"
                  onClick={() => setShowRegister(false)}
                  className="rounded-md border border-white/25 px-2 py-1 text-xs text-white/85 hover:bg-white/10"
                >
                  Close
                </button>
              </div>

              <form onSubmit={handleRegister} className="space-y-3">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-white/90">
                    Username
                  </label>
                  <input
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
                    placeholder="e.g. dhiraj"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-white/90">
                    Password
                  </label>
                  <input
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    type="password"
                    className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
                    placeholder="Minimum 8 characters"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-white/90">
                    Confirm password
                  </label>
                  <input
                    value={regConfirm}
                    onChange={(e) => setRegConfirm(e.target.value)}
                    type="password"
                    className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={regLoading}
                  className="mt-2 w-full rounded-md bg-white px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-white/90 disabled:opacity-60"
                >
                  {regLoading ? "Creating..." : "Register"}
                </button>
              </form>

              {regError ? (
                <p className="mt-3 rounded-md border border-red-300/45 bg-red-500/15 p-2 text-sm text-red-100">
                  {regError}
                </p>
              ) : null}

              {regMessage ? (
                <p className="mt-3 rounded-md border border-emerald-300/45 bg-emerald-500/15 p-2 text-sm text-emerald-100">
                  {regMessage}
                </p>
              ) : null}
            </motion.div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
