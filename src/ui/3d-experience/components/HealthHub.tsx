'use client'

import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, RoundedBox } from '@react-three/drei'
import * as THREE from 'three'

interface HealthHubProps {
  selectedPatient: string | null
  selectedDoctor: string | null
}

export default function HealthHub({ selectedPatient, selectedDoctor }: HealthHubProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)
  
  // Pulse animation based on activity
  useFrame((state) => {
    if (meshRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05
      meshRef.current.scale.setScalar(hovered ? scale * 1.1 : scale)
      
      // Rotation
      meshRef.current.rotation.y += 0.01
    }
  })
  
  // Color based on selection state
  const baseColor = selectedPatient && selectedDoctor 
    ? '#00ff88'  // Active - booking in progress
    : selectedPatient || selectedDoctor 
      ? '#4a9eff'  // Partial - one selected
      : '#6366f1'  // Default - idle
  
  return (
    <group>
      {/* Main Hub Sphere */}
      <mesh
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
      >
        <icosahedronGeometry args={[1.5, 1]} />
        <meshStandardMaterial
          color={baseColor}
          metalness={0.8}
          roughness={0.2}
          emissive={baseColor}
          emissiveIntensity={0.3}
        />
      </mesh>
      
      {/* Inner Glow */}
      <mesh scale={1.2}>
        <icosahedronGeometry args={[1.5, 1]} />
        <meshBasicMaterial
          color={baseColor}
          transparent
          opacity={0.1}
          side={THREE.BackSide}
        />
      </mesh>
      
      {/* Ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2, 0.05, 16, 100]} />
        <meshStandardMaterial
          color='#4a9eff'
          metalness={0.9}
          roughness={0.1}
          emissive='#4a9eff'
          emissiveIntensity={0.5}
        />
      </mesh>
      
      {/* Labels */}
      <Text
        position={[0, 2.5, 0]}
        fontSize={0.4}
        color='#ffffff'
        anchorX='center'
        anchorY='middle'
        font='/fonts/inter.woff'
      >
        DOCSYNC
      </Text>
      
      <Text
        position={[0, 2, 0]}
        fontSize={0.2}
        color='#888888'
        anchorX='center'
        anchorY='middle'
      >
        Healthcare Coordination Hub
      </Text>
      
      {/* Status indicator */}
      <group position={[0, -2, 0]}>
        <RoundedBox args={[2, 0.5, 0.3]} radius={0.1} position={[0, 0, 0]}>
          <meshStandardMaterial
            color='#1a1a2e'
            metalness={0.5}
            roughness={0.5}
          />
        </RoundedBox>
        <Text
          position={[0, 0, 0.16]}
          fontSize={0.15}
          color={selectedPatient && selectedDoctor ? '#00ff88' : '#4a9eff'}
          anchorX='center'
          anchorY='middle'
        >
          {selectedPatient && selectedDoctor 
            ? '● Booking Active' 
            : selectedPatient || selectedDoctor 
              ? '● Select Doctor' 
              : '● Awaiting Selection'}
        </Text>
      </group>
    </group>
  )
}
