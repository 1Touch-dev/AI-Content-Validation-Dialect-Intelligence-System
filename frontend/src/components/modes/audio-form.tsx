"use client";

import { FormEvent, useState } from "react";
import { backendFetch } from "@/lib/backend-auth";
import { TARGET_COUNTRIES, TargetCountry } from "@/lib/target-country";

type AudioResult = {
  transcript: string;
  dialect_prediction: string;
  dialect_confidence: number;
  dialect_check: string;
};

export default function AudioValidationForm() {
  const [targetCountry, setTargetCountry] = useState<TargetCountry>("honduras");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioPath, setAudioPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AudioResult | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      let res: Response;

      if (selectedFile) {
        const formData = new FormData();
        formData.append("target_country", targetCountry);
        formData.append("audio", selectedFile);
        res = await backendFetch("/validate-audio-upload", {
          method: "POST",
          body: formData,
        });
      } else {
        if (!audioPath.trim()) {
          setError("Please upload an audio file or provide an audio path.");
          setLoading(false);
          return;
        }
        res = await backendFetch("/validate-audio", {
          method: "POST",
          body: JSON.stringify({
            audio_path: audioPath,
            target_country: targetCountry,
          }),
        });
      }

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
      <form
        onSubmit={onSubmit}
        className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl"
      >
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-white/90">Audio Input</h4>
          <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-xs text-white/70">
            Whisper + Dialect
          </span>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Select Target Country</label>
          <select
            value={targetCountry}
            onChange={(e) => setTargetCountry(e.target.value as TargetCountry)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-indigo-300/70"
          >
            {TARGET_COUNTRIES.map((country) => (
              <option key={country.value} value={country.value} className="bg-[#0b1020] text-white">
                {country.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Upload Audio</label>
          <input
            type="file"
            accept="audio/mpeg,audio/mp3,audio/wav,audio/x-wav,audio/m4a,audio/mp4,audio/ogg"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white file:mr-3 file:rounded-md file:border-0 file:bg-white file:px-3 file:py-1 file:text-xs file:font-semibold file:text-black"
          />
          <p className="text-xs text-white/60">Optional fallback: use local audio path below.</p>
        </div>
        <input
          value={audioPath}
          onChange={(e) => setAudioPath(e.target.value)}
          placeholder="C:\\audio\\sample.wav"
          className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white"
        />
        <button className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-black" disabled={loading}>
          {loading ? "Validating..." : "Validate Audio"}
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
              {result.dialect_check.toUpperCase()}
            </span>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Dialect Prediction</p>
              <p className="mt-1 text-sm font-medium text-white/90">{result.dialect_prediction}</p>
            </div>
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Dialect Confidence</p>
              <p className="mt-1 text-xl font-semibold">{(result.dialect_confidence * 100).toFixed(2)}%</p>
            </div>
          </div>
          <div className="rounded-xl border border-white/15 bg-white/6 p-3">
            <p className="text-xs uppercase tracking-[0.14em] text-white/60">Transcript</p>
            <p className="mt-1 text-sm text-white/90">{result.transcript || "No transcript returned."}</p>
          </div>
          <div>
            <div className="mb-1 flex items-center justify-between text-xs text-white/65">
              <span>Dialect Confidence Meter</span>
              <span>{(result.dialect_confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 rounded-full bg-white/15">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-cyan-300 to-indigo-300"
                style={{ width: `${Math.min(100, Math.max(0, result.dialect_confidence * 100))}%` }}
              />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
