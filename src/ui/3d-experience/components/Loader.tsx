'use client'

import { Html, useProgress } from '@react-three/drei'

export default function Loader() {
  const { progress } = useProgress()
  
  return (
    <Html center>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        color: '#ffffff',
        fontFamily: 'system-ui, sans-serif'
      }}>
        <div style={{
          width: '200px',
          height: '4px',
          background: '#1a1a2e',
          borderRadius: '2px',
          overflow: 'hidden',
          marginBottom: '16px'
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #4a9eff, #6366f1)',
            transition: 'width 0.3s ease'
          }} />
        </div>
        <div style={{ fontSize: '14px', color: '#888' }}>
          Loading DocSync 3D...
        </div>
      </div>
    </Html>
  )
}
