'use client'

import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float, Text, Environment, ContactShadows } from '@react-three/drei'
import * as THREE from 'three'
import HealthHub from './HealthHub'
import PatientNode from './PatientNode'
import DoctorNode from './DoctorNode'
import ConnectionLines from './ConnectionLines'

// Sample data for visualization
const SAMPLE_PATIENTS = [
  { id: '1', name: 'Patient A', status: 'symptoms_detected', severity: 'moderate' },
  { id: '2', name: 'Patient B', status: 'reasoning', severity: 'mild' },
  { id: '3', name: 'Patient C', status: 'booking', severity: 'mild' },
]

const SAMPLE_DOCTORS = [
  { id: 'd1', name: 'Dr. Sharma', specialty: 'General Physician', available: true },
  { id: 'd2', name: 'Dr. Kumar', specialty: 'Internal Medicine', available: true },
]

export default function Scene() {
  const groupRef = useRef<THREE.Group>(null)
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null)
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null)
  
  // Slow rotation for ambient feel
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.1
    }
  })
  
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight 
        position={[10, 10, 5]} 
        intensity={1} 
        castShadow
        shadow-mapSize={[1024, 1024]}
      />
      <pointLight position={[-10, -10, -5]} intensity={0.5} color='#4a9eff' />
      
      {/* Environment */}
      <Environment preset='night' />
      <fog attach='fog' args={['#0a0a1a', 10, 50]} />
      
      {/* Main content group */}
      <group ref={groupRef}>
        {/* Central Health Hub */}
        <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
          <HealthHub 
            selectedPatient={selectedPatient}
            selectedDoctor={selectedDoctor}
          />
        </Float>
        
        {/* Patient Nodes (left side) */}
        <group position={[-5, 0, 0]}>
          {SAMPLE_PATIENTS.map((patient, index) => (
            <PatientNode
              key={patient.id}
              patient={patient}
              index={index}
              total={SAMPLE_PATIENTS.length}
              onSelect={() => setSelectedPatient(
                selectedPatient === patient.id ? null : patient.id
              )}
              isSelected={selectedPatient === patient.id}
            />
          ))}
        </group>
        
        {/* Doctor Nodes (right side) */}
        <group position={[5, 0, 0]}>
          {SAMPLE_DOCTORS.map((doctor, index) => (
            <DoctorNode
              key={doctor.id}
              doctor={doctor}
              index={index}
              total={SAMPLE_DOCTORS.length}
              onSelect={() => setSelectedDoctor(
                selectedDoctor === doctor.id ? null : doctor.id
              )}
              isSelected={selectedDoctor === doctor.id}
            />
          ))}
        </group>
        
        {/* Connection Lines */}
        <ConnectionLines 
          patients={SAMPLE_PATIENTS}
          doctors={SAMPLE_DOCTORS}
          selectedPatient={selectedPatient}
          selectedDoctor={selectedDoctor}
        />
      </group>
      
      {/* Ground shadow */}
      <ContactShadows 
        position={[0, -2.5, 0]} 
        opacity={0.4} 
        scale={20} 
        blur={2} 
        far={10}
      />
      
      {/* Floor Grid */}
      <gridHelper args={[30, 30, '#1a3a5c', '#0a1a2a']} position={[0, -2.49, 0]} />
    </>
  )
}
