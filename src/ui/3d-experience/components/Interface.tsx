'use client'

import { useState } from 'react'

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

const SAMPLE_PATIENTS: Patient[] = [
  { id: '1', name: 'Patient A', status: 'symptoms_detected', severity: 'moderate' },
  { id: '2', name: 'Patient B', status: 'reasoning', severity: 'mild' },
  { id: '3', name: 'Patient C', status: 'booking', severity: 'mild' },
]

const SAMPLE_DOCTORS: Doctor[] = [
  { id: 'd1', name: 'Dr. Sharma', specialty: 'General Physician', available: true },
  { id: 'd2', name: 'Dr. Kumar', specialty: 'Internal Medicine', available: true },
]

const STATUS_LABELS: Record<string, string> = {
  symptoms_detected: 'Symptoms Detected',
  reasoning: 'Clinical Reasoning',
  booking: 'Booking Confirmed',
}

export default function Interface() {
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null)
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'patients' | 'doctors'>('patients')
  
  const canBook = selectedPatient && selectedDoctor
  
  const handleBook = () => {
    if (canBook) {
      alert(`Booking appointment:\nPatient: ${selectedPatient}\nDoctor: ${selectedDoctor}`)
    }
  }
  
  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      fontFamily: 'system-ui, sans-serif',
      color: '#ffffff'
    }}>
      {/* Header */}
      <div style={{
        position: 'absolute',
        top: '24px',
        left: '24px',
        pointerEvents: 'auto'
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: 600,
          margin: 0,
          background: 'linear-gradient(135deg, #4a9eff, #6366f1)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          DocSync 3D Dashboard
        </h1>
        <p style={{
          fontSize: '12px',
          color: '#666',
          margin: '4px 0 0 0'
        }}>
          Healthcare Coordination Visualization
        </p>
      </div>
      
      {/* Stats */}
      <div style={{
        position: 'absolute',
        top: '24px',
        right: '24px',
        display: 'flex',
        gap: '24px',
        pointerEvents: 'auto'
      }}>
        <StatCard label='Active Patients' value='3' color='#4a9eff' />
        <StatCard label='In Reasoning' value='1' color='#8b5cf6' />
        <StatCard label='Available Doctors' value='2' color='#10b981' />
      </div>
      
      {/* Control Panel */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        left: '24px',
        width: '320px',
        background: 'rgba(10, 10, 26, 0.9)',
        borderRadius: '16px',
        border: '1px solid rgba(74, 158, 255, 0.2)',
        backdropFilter: 'blur(10px)',
        pointerEvents: 'auto',
        overflow: 'hidden'
      }}>
        {/* Tabs */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid rgba(255,255,255,0.1)'
        }}>
          {(['patients', 'doctors'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                flex: 1,
                padding: '12px',
                background: activeTab === tab ? 'rgba(74, 158, 255, 0.2)' : 'transparent',
                border: 'none',
                color: activeTab === tab ? '#4a9eff' : '#666',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500,
                textTransform: 'capitalize'
              }}
            >
              {tab}
            </button>
          ))}
        </div>
        
        {/* List */}
        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {activeTab === 'patients' 
            ? SAMPLE_PATIENTS.map(patient => (
                <div
                  key={patient.id}
                  onClick={() => setSelectedPatient(
                    selectedPatient === patient.id ? null : patient.id
                  )}
                  style={{
                    padding: '12px 16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    background: selectedPatient === patient.id 
                      ? 'rgba(74, 158, 255, 0.2)' 
                      : 'transparent',
                    borderLeft: selectedPatient === patient.id 
                      ? '3px solid #4a9eff' 
                      : '3px solid transparent'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 500 }}>
                      {patient.name}
                    </div>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      {STATUS_LABELS[patient.status]}
                    </div>
                  </div>
                  <SeverityBadge severity={patient.severity} />
                </div>
              ))
            : SAMPLE_DOCTORS.map(doctor => (
                <div
                  key={doctor.id}
                  onClick={() => doctor.available && setSelectedDoctor(
                    selectedDoctor === doctor.id ? null : doctor.id
                  )}
                  style={{
                    padding: '12px 16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: doctor.available ? 'pointer' : 'not-allowed',
                    opacity: doctor.available ? 1 : 0.5,
                    background: selectedDoctor === doctor.id 
                      ? 'rgba(16, 185, 129, 0.2)' 
                      : 'transparent',
                    borderLeft: selectedDoctor === doctor.id 
                      ? '3px solid #10b981' 
                      : '3px solid transparent'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 500 }}>
                      {doctor.name}
                    </div>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      {doctor.specialty}
                    </div>
                  </div>
                  <AvailabilityBadge available={doctor.available} />
                </div>
              ))
          }
        </div>
        
        {/* Book Button */}
        <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <button
            onClick={handleBook}
            disabled={!canBook}
            style={{
              width: '100%',
              padding: '12px',
              background: canBook 
                ? 'linear-gradient(135deg, #10b981, #059669)' 
                : '#333',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 600,
              cursor: canBook ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s ease'
            }}
          >
            {canBook ? 'Confirm Booking' : 'Select Patient & Doctor'}
          </button>
        </div>
      </div>
      
      {/* Instructions */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        right: '24px',
        fontSize: '11px',
        color: '#444',
        textAlign: 'right',
        pointerEvents: 'none'
      }}>
        <p style={{ margin: '0 0 4px 0' }}>🖱️ Click nodes to select</p>
        <p style={{ margin: 0 }}>🔄 Scene auto-rotates</p>
      </div>
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{
      background: 'rgba(10, 10, 26, 0.8)',
      borderRadius: '12px',
      padding: '12px 20px',
      border: `1px solid ${color}33`,
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '24px', fontWeight: 700, color }}>
        {value}
      </div>
      <div style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase' }}>
        {label}
      </div>
    </div>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    mild: '#22c55e',
    moderate: '#f59e0b',
    severe: '#ef4444'
  }
  
  return (
    <span style={{
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: 600,
      background: `${colors[severity]}22`,
      color: colors[severity],
      textTransform: 'uppercase'
    }}>
      {severity}
    </span>
  )
}

function AvailabilityBadge({ available }: { available: boolean }) {
  return (
    <span style={{
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: 600,
      background: available ? '#10b98122' : '#6b728022',
      color: available ? '#10b981' : '#6b7280'
    }}>
      {available ? 'Available' : 'Busy'}
    </span>
  )
}
