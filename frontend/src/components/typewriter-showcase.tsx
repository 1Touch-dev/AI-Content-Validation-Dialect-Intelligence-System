"use client";

import { useEffect, useState } from "react";

const TERMINAL_LINES = [
  "$ validate --asset campaign_video.mp4 --target honduras",
  "Loading Whisper, Dialect Model, and CLIP...",
  "Transcription complete. Dialect confidence: 93.2%",
  "Visual score complete. Context match: 88.1%",
  "Final decision: PASS",
];

export default function TypewriterShowcase() {
  const [lineCount, setLineCount] = useState(1);

  useEffect(() => {
    const id = setInterval(() => {
      setLineCount((prev) => (prev % TERMINAL_LINES.length) + 1);
    }, 1150);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="mt-8 w-full space-y-4">
    

      <div className="rounded-2xl border border-white/20 bg-black/40 p-5 text-left font-mono text-xs text-indigo-100 shadow-[0_12px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl md:text-sm">
        <div className="mb-3 flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-red-400/90" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-300/90" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/90" />
          <span className="ml-2 text-[11px] uppercase tracking-[0.2em] text-white/50">Live Pipeline</span>
        </div>
        <div className="space-y-1">
          {TERMINAL_LINES.slice(0, lineCount).map((line, index) => (
            <p key={`${line}-${index}`} className="text-white/85">
              {line}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
