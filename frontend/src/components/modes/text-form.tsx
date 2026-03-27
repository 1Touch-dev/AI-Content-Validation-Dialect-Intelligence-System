"use client";

import { FormEvent, useState } from "react";
import { backendFetch } from "@/lib/backend-auth";
import { getDefaultText, TARGET_COUNTRIES, TargetCountry } from "@/lib/target-country";

type TextResult = {
  dialect_prediction: string;
  dialect_confidence: number;
  dialect_check: string;
};

export default function TextValidationForm() {
  const [targetCountry, setTargetCountry] = useState<TargetCountry>("honduras");
  const [text, setText] = useState(getDefaultText("honduras"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<TextResult | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await backendFetch("/validate-text", {
        method: "POST",
        body: JSON.stringify({ text, target_country: targetCountry }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body?.detail || "Validation failed");
        return;
      }
      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-white/90">Text Input</label>
          <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-xs text-white/70">
            Dialect Engine
          </span>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Select Target Country</label>
          <select
            value={targetCountry}
            onChange={(e) => {
              const nextCountry = e.target.value as TargetCountry;
              setTargetCountry(nextCountry);
              setText(getDefaultText(nextCountry));
            }}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70"
          >
            {TARGET_COUNTRIES.map((country) => (
              <option key={country.value} value={country.value} className="bg-[#0b1020] text-white">
                {country.label}
              </option>
            ))}
          </select>
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70"
        />
        <button className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-black" disabled={loading}>
          {loading ? "Validating..." : "Validate Text"}
        </button>
      </form>
      {error ? <div className="rounded-xl border border-red-300/45 bg-red-500/15 p-3 text-sm text-red-100">{error}</div> : null}
      {result ? (
        <div className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Validation Result</h4>
            <span
              className={
                result.dialect_check === "pass"
                  ? "rounded-full border border-emerald-300/40 bg-emerald-500/20 px-2.5 py-1 text-xs font-semibold uppercase text-emerald-200"
                  : "rounded-full border border-red-300/40 bg-red-500/20 px-2.5 py-1 text-xs font-semibold uppercase text-red-200"
              }
            >
              {result.dialect_check}
            </span>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Dialect</p>
              <p className="mt-1 text-xl font-semibold">{result.dialect_prediction}</p>
            </div>
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Confidence</p>
              <p className="mt-1 text-xl font-semibold">
                {(result.dialect_confidence * 100).toFixed(2)}%
              </p>
            </div>
          </div>
          <div>
            <div className="mb-1 flex items-center justify-between text-xs text-white/65">
              <span>Confidence Meter</span>
              <span>{(result.dialect_confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 rounded-full bg-white/15">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-indigo-300 to-fuchsia-300"
                style={{ width: `${Math.min(100, Math.max(0, result.dialect_confidence * 100))}%` }}
              />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
