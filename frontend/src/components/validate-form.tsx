"use client";

import { FormEvent, useEffect, useState } from "react";
import { motion } from "motion/react";
import { backendFetch } from "@/lib/backend-auth";

type ValidationData = {
  transcript: string;
  dialect_prediction: string;
  dialect_confidence: number;
  content_match_score: number;
  validation_status: string;
};

const COUNTRY_OPTIONS = [
  { value: "honduras", label: "Honduras 🇭🇳", defaultTopic: "Honduras scenery, beautiful people" },
  { value: "ecuador", label: "Ecuador 🇪🇨", defaultTopic: "Ecuador scenery, beautiful people" },
];

export default function ValidateForm() {
  const [targetCountry, setTargetCountry] = useState("honduras");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPath, setVideoPath] = useState("");
  const [expectedTopic, setExpectedTopic] = useState("Honduras scenery, beautiful people");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ValidationData | null>(null);

  useEffect(() => {
    const selected = COUNTRY_OPTIONS.find((country) => country.value === targetCountry);
    if (selected) setExpectedTopic(selected.defaultTopic);
  }, [targetCountry]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      let res: Response;
      if (selectedFile) {
        const formData = new FormData();
        formData.append("expected_topic", expectedTopic);
        formData.append("target_country", targetCountry);
        formData.append("video", selectedFile);
        res = await backendFetch("/validate-video-upload", {
          method: "POST",
          body: formData,
        });
      } else {
        if (!videoPath.trim()) {
          setError("Please upload a video or provide a video path.");
          setLoading(false);
          return;
        }
        res = await backendFetch("/validate-video", {
          method: "POST",
          body: JSON.stringify({
            video_path: videoPath,
            expected_topic: expectedTopic,
            target_country: targetCountry,
          }),
        });
      }
      const body = await res.json();
      if (!res.ok) {
        setError(body?.detail || "Validation request failed.");
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
      <motion.form
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        onSubmit={handleSubmit}
        className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl"
      >
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.2em] text-white/65">
            New Validation
          </p>
          <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-xs text-white/70">
            Full Pipeline
          </span>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Target Country</label>
          <select
            value={targetCountry}
            onChange={(e) => setTargetCountry(e.target.value)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white"
          >
            {COUNTRY_OPTIONS.map((country) => (
              <option key={country.value} value={country.value} className="bg-[#0b1020] text-white">
                {country.label}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Upload Video</label>
          <input
            type="file"
            accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white file:mr-3 file:rounded-md file:border-0 file:bg-white file:px-3 file:py-1 file:text-xs file:font-semibold file:text-black"
          />
          <p className="text-xs text-white/60">Optional fallback: use local video path below.</p>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Video Path</label>
          <input
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            placeholder="C:\\videos\\sample.mp4"
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/45 outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-white/90">Expected Topic</label>
          <input
            value={expectedTopic}
            onChange={(e) => setExpectedTopic(e.target.value)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/45 outline-none focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-black transition hover:bg-white/90 disabled:opacity-60"
        >
          {loading ? "Validating..." : "Validate Video"}
        </button>
      </motion.form>

      {error ? (
        <div className="rounded-xl border border-red-300/45 bg-red-500/15 p-4 text-sm text-red-100">
          {error}
        </div>
      ) : null}

      {result ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Validation Result</h2>
            <span
              className={
                result.validation_status === "PASS"
                  ? "rounded-full border border-emerald-300/40 bg-emerald-500/20 px-2.5 py-1 text-xs font-semibold uppercase text-emerald-200"
                  : "rounded-full border border-red-300/40 bg-red-500/20 px-2.5 py-1 text-xs font-semibold uppercase text-red-200"
              }
            >
              {result.validation_status}
            </span>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Dialect</p>
              <p className="mt-1 text-lg font-semibold">{result.dialect_prediction}</p>
            </div>
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Dialect Confidence</p>
              <p className="mt-1 text-lg font-semibold">
                {(result.dialect_confidence * 100).toFixed(2)}%
              </p>
            </div>
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Visual Score</p>
              <p className="mt-1 text-lg font-semibold">
                {(result.content_match_score * 100).toFixed(2)}%
              </p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <div className="mb-1 flex items-center justify-between text-xs text-white/65">
                <span>Dialect Meter</span>
                <span>{(result.dialect_confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 rounded-full bg-white/15">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-indigo-300 to-fuchsia-300"
                  style={{ width: `${Math.min(100, Math.max(0, result.dialect_confidence * 100))}%` }}
                />
              </div>
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between text-xs text-white/65">
                <span>Visual Meter</span>
                <span>{(result.content_match_score * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 rounded-full bg-white/15">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-cyan-300 to-indigo-300"
                  style={{ width: `${Math.min(100, Math.max(0, result.content_match_score * 100))}%` }}
                />
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-white/15 bg-black/25 p-3 text-sm text-white/90">
            <p className="text-xs uppercase tracking-[0.14em] text-white/60">Transcript</p>
            <p className="mt-1">{result.transcript || "-"}</p>
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}
