"use client";

import { FormEvent, useState } from "react";
import { motion } from "motion/react";
import { backendFetch } from "@/lib/backend-auth";
import { getDefaultTopic, TARGET_COUNTRIES, TargetCountry } from "@/lib/target-country";

type ValidationData = {
  transcript: string;
  dialect_prediction: string;
  dialect_confidence: number;
  content_match_score: number;
  validation_status: string;
  validation_score?: number;
  dialect_check?: string;
  detected_language?: string;
  expected_content?: string;
  geographic_verification?: boolean;
  detected_entities?: string[];
};

export default function ValidateForm() {
  const [targetCountry, setTargetCountry] = useState<TargetCountry>("honduras");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPath, setVideoPath] = useState("");
  const [expectedTopic, setExpectedTopic] = useState(getDefaultTopic("honduras"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ValidationData | null>(null);

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
          <label className="text-sm font-medium text-white/90">Select Target Country</label>
          <select
            value={targetCountry}
            onChange={(e) => {
              const nextCountry = e.target.value as TargetCountry;
              setTargetCountry(nextCountry);
              setExpectedTopic(getDefaultTopic(nextCountry));
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

          <div className="rounded-xl border border-white/15 bg-black/25 p-4 text-sm text-white/90">
            <p className="text-xs uppercase tracking-[0.14em] text-white/60">Detailed Report</p>
            <div className="mt-3 space-y-2 whitespace-pre-wrap leading-relaxed">
              <p>Final Validation Score</p>
              <p className="text-base font-semibold">
                {((result.validation_score ?? 0) * 100).toFixed(2)}%
              </p>
              <p>
                Status:{" "}
                <span className={result.validation_status === "PASS" ? "text-emerald-200" : "text-red-200"}>
                  {result.validation_status}
                </span>
              </p>
              <p className="pt-1 text-white/95">Process Breakdown</p>
              <p>🗣️ Audio Layer (large-v3-turbo + HF):</p>
              <p>
                Transcript: &apos;{result.transcript || "-"}&apos;
                {result.detected_language ? ` [Detected: ${result.detected_language}]` : ""}
              </p>
              <p>
                Dialect Found: {result.dialect_prediction} ({(result.dialect_check || "fail").toUpperCase()})
              </p>
              <p>👁️ Vision Layer (CLIP + OCR):</p>
              <p>Context Evaluated: &apos;{result.expected_content || expectedTopic}&apos;</p>
              <p>Semantic Match: {(result.content_match_score ?? 0).toFixed(4)}</p>
              <p>🌍 Geographic & Localism Verification:</p>
              {result.geographic_verification === false ? (
                <>
                  <p>⚠️ Geographic Mismatch! Detected international entities: {JSON.stringify(result.detected_entities || [])}</p>
                  <p>Validation fail: Video content belongs to a different geographic region (e.g., European sports).</p>
                </>
              ) : (
                <p>✅ Geographic context appears aligned with selected target country.</p>
              )}
            </div>
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}
