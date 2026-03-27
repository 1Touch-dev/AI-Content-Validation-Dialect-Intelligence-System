"use client";

import { FormEvent, useEffect, useState } from "react";
import { backendFetch } from "@/lib/backend-auth";

type ImageResult = {
  expected_topic: string;
  content_match_score: number;
  validation_status: string;
};

const COUNTRY_OPTIONS = [
  { value: "honduras", label: "Honduras 🇭🇳", defaultTopic: "Honduras scenery, beautiful people" },
  { value: "ecuador", label: "Ecuador 🇪🇨", defaultTopic: "Ecuador scenery, beautiful people" },
];

export default function ImageValidationForm() {
  const [targetCountry, setTargetCountry] = useState("honduras");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePath, setImagePath] = useState("");
  const [expectedTopic, setExpectedTopic] = useState("Honduras scenery, beautiful people");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ImageResult | null>(null);

  useEffect(() => {
    const selected = COUNTRY_OPTIONS.find((country) => country.value === targetCountry);
    if (selected) setExpectedTopic(selected.defaultTopic);
  }, [targetCountry]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      let res: Response;
      if (selectedFile) {
        const formData = new FormData();
        formData.append("expected_topic", expectedTopic);
        formData.append("target_country", targetCountry);
        formData.append("image", selectedFile);
        res = await backendFetch("/validate-image-upload", {
          method: "POST",
          body: formData,
        });
      } else {
        if (!imagePath.trim()) {
          setError("Please upload an image or provide an image path.");
          setLoading(false);
          return;
        }
        res = await backendFetch("/validate-image", {
          method: "POST",
          body: JSON.stringify({
            image_path: imagePath,
            expected_topic: expectedTopic,
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
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-white/90">Image Input</h4>
          <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-xs text-white/70">
            OCR + CLIP
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
          <label className="text-sm font-medium text-white/90">Upload Image</label>
          <input
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white file:mr-3 file:rounded-md file:border-0 file:bg-white file:px-3 file:py-1 file:text-xs file:font-semibold file:text-black"
          />
          <p className="text-xs text-white/60">Optional fallback: use local image path below.</p>
        </div>
        <input
          value={imagePath}
          onChange={(e) => setImagePath(e.target.value)}
          placeholder="C:\\images\\sample.jpg"
          className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white"
        />
        <input
          value={expectedTopic}
          onChange={(e) => setExpectedTopic(e.target.value)}
          className="w-full rounded-md border border-white/25 bg-black/20 px-3 py-2 text-sm text-white"
          required
        />
        <button className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-black" disabled={loading}>
          {loading ? "Validating..." : "Validate Image"}
        </button>
      </form>
      {error ? <div className="rounded-xl border border-red-300/45 bg-red-500/15 p-3 text-sm text-red-100">{error}</div> : null}
      {result ? (
        <div className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Validation Result</h4>
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
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Expected Topic</p>
              <p className="mt-1 text-sm font-medium text-white/90">{result.expected_topic}</p>
            </div>
            <div className="rounded-xl border border-white/15 bg-white/6 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-white/60">Match Score</p>
              <p className="mt-1 text-xl font-semibold">
                {(result.content_match_score * 100).toFixed(2)}%
              </p>
            </div>
          </div>
          <div>
            <div className="mb-1 flex items-center justify-between text-xs text-white/65">
              <span>Visual Relevance Meter</span>
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
      ) : null}
    </div>
  );
}
