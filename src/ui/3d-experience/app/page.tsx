'use client'

import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import Scene from '@/components/Scene'
import Loader from '@/components/Loader'
import Interface from '@/components/Interface'

export default function Home() {
  return (
    <main style={{ width: '100vw', height: '100vh', background: '#0a0a1a' }}>
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 2, 8], fov: 50 }}
        dpr={[1, 2]}
        gl={{ antialias: true }}
      >
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
      
      {/* 2D UI Overlay */}
      <Interface />
    </main>
  )
}
