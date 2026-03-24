"use client";

import Link from "next/link";
import { motion } from "motion/react";
import gsap from "gsap";
import { useEffect, useRef, useState } from "react";
import ThreeLandingBg from "@/components/three-landing-bg";
import TypewriterShowcase from "@/components/typewriter-showcase";

const HERO_TYPEWRITER_TEXT = "AI Validation Console for Dialect, Audio, Image, and Video";

export default function LandingHero() {
  const badgeRef = useRef<HTMLDivElement>(null);
  const orbLeftRef = useRef<HTMLDivElement>(null);
  const orbRightRef = useRef<HTMLDivElement>(null);
  const [heroCharIdx, setHeroCharIdx] = useState(0);

  useEffect(() => {
    if (!badgeRef.current) return;
    gsap.to(badgeRef.current, {
      y: -8,
      duration: 2,
      ease: "sine.inOut",
      repeat: -1,
      yoyo: true,
    });

    if (orbLeftRef.current) {
      gsap.to(orbLeftRef.current, {
        x: 18,
        y: -16,
        duration: 3.2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    }

    if (orbRightRef.current) {
      gsap.to(orbRightRef.current, {
        x: -20,
        y: 14,
        duration: 3.6,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    }

  }, []);

  useEffect(() => {
    if (heroCharIdx >= HERO_TYPEWRITER_TEXT.length) return;

    const id = setTimeout(() => {
      setHeroCharIdx((prev) => prev + 1);
    }, 40);

    return () => clearTimeout(id);
  }, [heroCharIdx]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#060812] text-white selection:bg-indigo-300/40">
      <ThreeLandingBg />

      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(93,123,255,0.35),transparent_35%),radial-gradient(circle_at_80%_70%,rgba(197,78,255,0.25),transparent_45%)]" />
      <div
        ref={orbLeftRef}
        className="pointer-events-none absolute -left-20 top-32 h-72 w-72 rounded-full bg-indigo-500/25 blur-3xl"
      />
      <div
        ref={orbRightRef}
        className="pointer-events-none absolute -right-16 bottom-20 h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl"
      />

      <header className="relative z-20 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <div className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs tracking-[0.18em] uppercase backdrop-blur">
          AVDIS
        </div>
        <nav className="flex items-center gap-3 text-sm">
          <Link
            href="/login"
            className="rounded-md border border-white/25 bg-white/5 px-3 py-1.5 transition hover:bg-white/10"
          >
            Login
          </Link>
          <Link
            href="/dashboard"
            className="rounded-md bg-white px-3 py-1.5 font-semibold text-black transition hover:bg-white/90"
          >
            Dashboard
          </Link>
        </nav>
      </header>

      <section className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col items-center justify-center px-6 pb-20 pt-6">
        <motion.div
          ref={badgeRef}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-5 rounded-full border border-white/20 bg-white/10 px-4 py-1 text-xs tracking-[0.2em] uppercase backdrop-blur-md"
        >
          Dialect Intelligence Platform
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.08 }}
          className="max-w-5xl text-center text-4xl font-semibold leading-tight md:text-6xl"
        >
          <span className="bg-gradient-to-r from-indigo-200 to-fuchsia-200 bg-clip-text text-transparent">
            {HERO_TYPEWRITER_TEXT.slice(0, heroCharIdx)}
          </span>
          <span className="ml-1 inline-block h-[0.95em] w-[2px] animate-pulse bg-white/85 align-[-0.1em]" />
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.16 }}
          className="mt-5 max-w-3xl text-center text-base text-white/75 md:text-lg"
        >
          Validate campaign assets with a premium multi-modal workflow built for
          speed, consistency, and production-grade quality checks.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.34 }}
          className="mt-9 flex flex-wrap items-center justify-center gap-3"
        >
          <Link
            href="/login"
            className="rounded-md bg-white px-6 py-2.5 text-sm font-semibold text-black shadow-[0_8px_30px_rgba(255,255,255,0.2)] transition hover:bg-white/90"
          >
            Sign in
          </Link>
          <Link
            href="/dashboard"
            className="rounded-md border border-white/35 bg-white/5 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/10"
          >
            Open Dashboard
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.28 }}
          className="w-full max-w-5xl"
        >
          <TypewriterShowcase />
        </motion.div>

       
      </section>
    </main>
  );
}
