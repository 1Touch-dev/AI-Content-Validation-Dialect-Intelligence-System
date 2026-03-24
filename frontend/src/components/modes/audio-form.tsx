"use client";

export default function AudioValidationForm() {
  return (
    <div className="space-y-6">
      <section className="space-y-4 rounded-2xl border border-white/20 bg-gradient-to-br from-white/12 to-white/6 p-6 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-white/90">Audio Input</h4>
          <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-xs text-white/70">
            Whisper + Dialect
          </span>
        </div>

        <div className="rounded-xl border border-indigo-300/30 bg-indigo-500/15 p-5 text-center">
          <p className="text-xs uppercase tracking-[0.16em] text-indigo-200/90">
            Module Status
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Coming Soon</h3>
          <p className="mt-2 text-sm text-white/80">
            The Audio Validation experience is currently being rebuilt with a
            richer upload and preview workflow.
          </p>
        </div>
      </section>
    </div>
  );
}
