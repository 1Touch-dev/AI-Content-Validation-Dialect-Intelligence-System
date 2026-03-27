"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Points, PointMaterial } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

function ParticleField() {
  const pointsRef = useRef<THREE.Points>(null);
  const sphereRef = useRef<THREE.Mesh>(null);

  const positions = useMemo(() => {
    const count = 1200;
    const arr = new Float32Array(count * 3);

    const seeded = (i: number) => {
      const x = Math.sin(i * 12.9898) * 43758.5453;
      return x - Math.floor(x);
    };

    for (let i = 0; i < count; i++) {
      arr[i * 3] = (seeded(i * 3 + 1) - 0.5) * 18;
      arr[i * 3 + 1] = (seeded(i * 3 + 2) - 0.5) * 10;
      arr[i * 3 + 2] = (seeded(i * 3 + 3) - 0.5) * 12;
    }
    return arr;
  }, []);

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.02;
      pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.08;
    }
    if (sphereRef.current) {
      sphereRef.current.rotation.y = state.clock.elapsedTime * 0.18;
      sphereRef.current.rotation.x = state.clock.elapsedTime * 0.08;
    }
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight intensity={1} position={[2, 3, 2]} color="#7aa2ff" />
      <Float speed={1.2} rotationIntensity={0.5} floatIntensity={0.8}>
        <mesh ref={sphereRef} position={[0, 0.2, -1.8]}>
          <icosahedronGeometry args={[1.8, 1]} />
          <meshStandardMaterial
            color="#6f79ff"
            emissive="#4037b8"
            emissiveIntensity={0.35}
            wireframe
            transparent
            opacity={0.42}
          />
        </mesh>
      </Float>

      <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#8cc3ff"
          size={0.03}
          sizeAttenuation
          depthWrite={false}
          opacity={0.45}
        />
      </Points>
    </>
  );
}

export default function ThreeDashboardBg() {
  return (
    <div className="pointer-events-none absolute inset-0 opacity-80">
      <Canvas camera={{ position: [0, 0, 8], fov: 55 }}>
        <ParticleField />
      </Canvas>
    </div>
  );
}
