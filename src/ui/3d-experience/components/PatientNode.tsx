'use client'

import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, RoundedBox } from '@react-three/drei'
import * as THREE from 'three'

interface Patient {
  id: string
  name: string
  status: string
  severity: string
}

interface PatientNodeProps {
  patient: Patient
  index: number
  total: number
  onSelect: () => void
  isSelected: boolean
}

const STATUS_COLORS: Record<string, string> = {
  symptoms_detected: '#f59e0b',
  reasoning: '#8b5cf6',
  booking: '#10b981',
}

const STATUS_LABELS: Record<string, string> = {
  symptoms_detected: 'Symptoms',
  reasoning: 'Reasoning',
  booking: 'Booking',
}

export default function PatientNode({ 
  patient, 
  index, 
  total, 
  onSelect, 
  isSelected 
}: PatientNodeProps) {
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
      meshRef.current.position.y = y + Math.sin(state.clock.elapsedTime + index) * 0.1
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5 + index) * 0.1
    }
  })
  
  const color = STATUS_COLORS[patient.status] || '#4a9eff'
  
  return (
    <group position={[x, 0, 0]}>
      <mesh
        ref={meshRef}
        position={[0, y, 0]}
        onClick={onSelect}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
      >
        <capsuleGeometry args={[0.3, 0.6, 8, 16]} />
        <meshStandardMaterial
          color={color}
          metalness={0.6}
          roughness={0.3}
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
        position={[0, y + 0.8, 0]}
        fontSize={0.2}
        color='#ffffff'
        anchorX='center'
        anchorY='middle'
      >
        {patient.name}
      </Text>
      
      {/* Status badge */}
      <group position={[0, y - 0.8, 0]}>
        <RoundedBox args={[1.2, 0.35, 0.1]} radius={0.05}>
          <meshStandardMaterial
            color='#1a1a2e'
            metalness={0.3}
            roughness={0.7}
          />
        </RoundedBox>
        <Text
          position={[0, 0, 0.06]}
          fontSize={0.12}
          color={color}
          anchorX='center'
          anchorY='middle'
        >
          {STATUS_LABELS[patient.status] || patient.status}
        </Text>
      </group>
      
      {/* Severity indicator */}
      <Text
        position={[0.5, y, 0]}
        fontSize={0.15}
        color={patient.severity === 'severe' ? '#ef4444' : 
               patient.severity === 'moderate' ? '#f59e0b' : '#22c55e'}
        anchorX='left'
        anchorY='middle'
      >
        {patient.severity === 'severe' ? '!' : 
         patient.severity === 'moderate' ? '~' : '-'}
      </Text>
    </group>
  )
}
