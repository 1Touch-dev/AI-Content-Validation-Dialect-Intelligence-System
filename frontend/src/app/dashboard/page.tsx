import Link from "next/link";
import {
  AudioLines,
  BrainCircuit,
  CheckCircle2,
  Image as ImageIcon,
  Languages,
  Video,
} from "lucide-react";

export default function DashboardPage() {
  const cards = [
    {
      href: "/dashboard/text",
      title: "Text Validator",
      desc: "Classify dialect confidence from user-submitted Spanish text.",
      meta: "NLP Classifier",
      icon: Languages,
    },
    {
      href: "/dashboard/image",
      title: "Image Validator",
      desc: "OCR blacklist checks and CLIP-based semantic relevance scoring.",
      meta: "Vision + OCR",
      icon: ImageIcon,
    },
    {
      href: "/dashboard/audio",
      title: "Audio Validator",
      desc: "Whisper transcription plus dialect classification in one workflow.",
      meta: "ASR + NLP",
      icon: AudioLines,
    },
    {
      href: "/dashboard/video",
      title: "Video Validator",
      desc: "Complete media pipeline combining audio, dialect, and visual checks.",
      meta: "End-to-End",
      icon: Video,
    },
  ];

  return (
    <section className="space-y-7">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-white/15 bg-white/8 p-5">
          <p className="text-xs uppercase tracking-[0.16em] text-white/60">Modules</p>
          <p className="mt-1 text-2xl font-semibold">4</p>
        </div>
        <div className="rounded-xl border border-white/15 bg-white/8 p-5">
          <p className="text-xs uppercase tracking-[0.16em] text-white/60">Auth Model</p>
          <p className="mt-1 text-2xl font-semibold">Backend</p>
        </div>
        <div className="rounded-xl border border-white/15 bg-white/8 p-5">
          <p className="text-xs uppercase tracking-[0.16em] text-white/60">Workspace</p>
          <p className="mt-1 text-2xl font-semibold">Operational</p>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-2xl border border-white/15 bg-white/8 p-6 transition hover:-translate-y-0.5 hover:bg-white/15"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.16em] text-white/60">{card.meta}</p>
              <card.icon className="h-5 w-5 text-indigo-200" />
            </div>
            <h2 className="mt-2 text-xl font-semibold">{card.title}</h2>
            <p className="mt-2 text-sm text-white/75">{card.desc}</p>
            <p className="mt-4 text-sm font-medium text-indigo-200">Open module {"->"}</p>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-white/15 bg-white/8 p-4">
          <div className="flex items-center gap-2 text-white/70">
            <BrainCircuit className="h-4 w-4" />
            <p className="text-xs uppercase tracking-[0.14em]">Inference Stack</p>
          </div>
          <p className="mt-2 text-sm text-white/80">Whisper + Dialect + CLIP + OCR</p>
        </div>
        <div className="rounded-xl border border-white/15 bg-white/8 p-4">
          <div className="flex items-center gap-2 text-white/70">
            <CheckCircle2 className="h-4 w-4" />
            <p className="text-xs uppercase tracking-[0.14em]">Readiness</p>
          </div>
          <p className="mt-2 text-sm text-white/80">Production-oriented workflow enabled</p>
        </div>
        <div className="rounded-xl border border-white/15 bg-white/8 p-4">
          <div className="flex items-center gap-2 text-white/70">
            <Languages className="h-4 w-4" />
            <p className="text-xs uppercase tracking-[0.14em]">Dialect Scope</p>
          </div>
          <p className="mt-2 text-sm text-white/80">Honduras-focused binary validation</p>
        </div>
      </div>
    </section>
  );
}
