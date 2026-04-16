'use client'

import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, RoundedBox } from '@react-three/drei'
import * as THREE from 'three'

interface Doctor {
  id: string
  name: string
  specialty: string
  available: boolean
}

interface DoctorNodeProps {
  doctor: Doctor
  index: number
  total: number
  onSelect: () => void
  isSelected: boolean
}

export default function DoctorNode({ 
  doctor, 
  index, 
  total, 
  onSelect, 
  isSelected 
}: DoctorNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)
  
  // Calculate position in arc
  const angle = ((index / total) - 0.5) * Math.PI * 0.5
  const radius = 3
  const x = Math.cos(angle) * radius
  const y = Math.sin(angle) * radius * 0.5 + (index - (total - 1) / 2) * 0.8
  
  // Float animation
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = y + Math.sin(state.clock.elapsedTime + index + 2) * 0.1
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5 + index) * 0.1
    }
  })
  
  const color = doctor.available ? '#10b981' : '#6b7280'
  
  return (
    <group position={[x, 0, 0]}>
      <mesh
        ref={meshRef}
        position={[0, y, 0]}
        onClick={doctor.available ? onSelect : undefined}
        onPointerOver={() => doctor.available && setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
      >
        <cylinderGeometry args={[0.4, 0.4, 0.3, 32]} />
        <meshStandardMaterial
          color={color}
          metalness={0.7}
          roughness={0.2}
          emissive={color}
          emissiveIntensity={hovered || isSelected ? 0.5 : 0.2}
        />
      </mesh>
      
      {/* Selection ring */}
      {isSelected && (
        <mesh position={[0, y, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.6, 0.03, 16, 32]} />
          <meshBasicMaterial color={color} />
        </mesh>
      )}
      
      {/* Name label */}
      <Text
        position={[0, y + 0.7, 0]}
        fontSize={0.18}
        color='#ffffff'
        anchorX='center'
        anchorY='middle'
      >
        {doctor.name}
      </Text>
      
      {/* Specialty label */}
      <Text
        position={[0, y + 0.4, 0]}
        fontSize={0.12}
        color='#888888'
        anchorX='center'
        anchorY='middle'
      >
        {doctor.specialty}
      </Text>
      
      {/* Availability badge */}
      <group position={[0, y - 0.7, 0]}>
        <RoundedBox args={[1.4, 0.35, 0.1]} radius={0.05}>
          <meshStandardMaterial
            color='#1a1a2e'
            metalness={0.3}
            roughness={0.7}
          />
        </RoundedBox>
        <Text
          position={[0, 0, 0.06]}
          fontSize={0.1}
          color={doctor.available ? '#10b981' : '#6b7280'}
          anchorX='center'
          anchorY='middle'
        >
          {doctor.available ? '● Available' : '○ Unavailable'}
        </Text>
      </group>
    </group>
  )
}
