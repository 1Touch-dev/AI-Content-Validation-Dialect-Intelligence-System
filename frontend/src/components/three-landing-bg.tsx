"use client";

import { Canvas } from "@react-three/fiber";
import { Stars } from "@react-three/drei";

function HeroScene() {
  return (
    <>
      <Stars
        radius={70}
        depth={40}
        count={2600}
        factor={2.8}
        saturation={0}
        fade
        speed={0.4}
      />
    </>
  );
}

export default function ThreeLandingBg() {
  return (
    <div className="pointer-events-none absolute inset-0">
      <Canvas camera={{ position: [0, 0, 7], fov: 52 }}>
        <HeroScene />
      </Canvas>
    </div>
  );
}
