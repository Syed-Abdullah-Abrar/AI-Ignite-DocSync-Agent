'use client'

import { useMemo } from 'react'
import { Line } from '@react-three/drei'
import * as THREE from 'three'

interface Patient {
  id: string
  name: string
  status: string
  severity: string
}

interface Doctor {
  id: string
  name: string
  specialty: string
  available: boolean
}

interface ConnectionLinesProps {
  patients: Patient[]
  doctors: Doctor[]
  selectedPatient: string | null
  selectedDoctor: string | null
}

export default function ConnectionLines({ 
  patients, 
  doctors, 
  selectedPatient,
  selectedDoctor 
}: ConnectionLinesProps) {
  const lines = useMemo(() => {
    const result: {
      start: [number, number, number]
      end: [number, number, number]
      color: string
      opacity: number
    }[] = []
    
    // Hub center position
    const hubX = 0
    const hubY = 0
    
    patients.forEach((patient, pIndex) => {
      const total = patients.length
      const pAngle = ((pIndex / total) - 0.5) * Math.PI * 0.5
      const pRadius = 3
      const pX = hubX - Math.cos(pAngle) * pRadius
      const pY = Math.sin(pAngle) * pRadius * 0.5 + (pIndex - (total - 1) / 2) * 0.8
      
      // Connection to hub
      const isActive = selectedPatient === patient.id
      
      result.push({
        start: [pX, pY, 0],
        end: [hubX, hubY, 0],
        color: isActive ? '#4a9eff' : '#1a3a5c',
        opacity: isActive ? 0.8 : 0.3
      })
      
      // If patient and doctor selected, draw booking line
      if (selectedPatient === patient.id && selectedDoctor) {
        const dIndex = doctors.findIndex(d => d.id === selectedDoctor)
        const dTotal = doctors.length
        const dAngle = ((dIndex / dTotal) - 0.5) * Math.PI * 0.5
        const dRadius = 3
        const dX = hubX + Math.cos(dAngle) * dRadius
        const dY = Math.sin(dAngle) * dRadius * 0.5 + (dIndex - (dTotal - 1) / 2) * 0.8
        
        result.push({
          start: [hubX, hubY, 0],
          end: [dX, dY, 0],
          color: '#00ff88',
          opacity: 0.8
        })
      }
    })
    
    return result
  }, [patients, doctors, selectedPatient, selectedDoctor])
  
  return (
    <group>
      {lines.map((line, index) => (
        <Line
          key={index}
          points={[line.start, line.end]}
          color={line.color}
          lineWidth={2}
          transparent
          opacity={line.opacity}
          dashed={line.color === '#00ff88'}
          dashScale={10}
          dashSize={0.1}
          gapSize={0.1}
        />
      ))}
    </group>
  )
}
