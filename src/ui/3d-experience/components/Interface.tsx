'use client'

import { useState, useEffect } from 'react'
import ChatPanel from './ChatPanel'

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
  hospital?: string
  distance?: string
}

interface Stats {
  active_patients: number
  in_reasoning: number
  booking_confirmed: number
  available_doctors: number
}

const FALLBACK_PATIENTS: Patient[] = [
  { id: '1', name: 'Patient A', status: 'symptoms_detected', severity: 'moderate' },
  { id: '2', name: 'Patient B', status: 'reasoning', severity: 'mild' },
  { id: '3', name: 'Patient C', status: 'booking', severity: 'mild' },
]

const FALLBACK_DOCTORS: Doctor[] = [
  { id: 'd1', name: 'Dr. Sharma', specialty: 'General Physician', available: true },
  { id: 'd2', name: 'Dr. Kumar', specialty: 'Internal Medicine', available: true },
]

const FALLBACK_STATS: Stats = {
  active_patients: 3,
  in_reasoning: 1,
  booking_confirmed: 1,
  available_doctors: 2,
}

export default function Interface() {
  // Responsive state - hooks INSIDE the component
  const [isMobile, setIsMobile] = useState(false)
  
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])
  
  const STATUS_LABELS: Record<string, string> = {
    symptoms_detected: 'Symptoms Detected',
    reasoning: 'Clinical Reasoning',
    booking: 'Booking Confirmed',
  }
  
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null)
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'patients' | 'doctors'>('patients')
  const [patients, setPatients] = useState<Patient[]>(FALLBACK_PATIENTS)
  const [doctors, setDoctors] = useState<Doctor[]>(FALLBACK_DOCTORS)
  const [stats, setStats] = useState<Stats>(FALLBACK_STATS)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [bookingStatus, setBookingStatus] = useState<string | null>(null)
  const [showChat, setShowChat] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [chatSessionId, setChatSessionId] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{id: string, role: 'user' | 'assistant', content: string, timestamp: Date}>>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm DocSync, your healthcare assistant. Please describe your symptoms or health concern.",
      timestamp: new Date()
    }
  ])

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = `${window.location.protocol}//${window.location.hostname}:8000`

        const [patientsRes, doctorsRes, statsRes] = await Promise.all([
          fetch(`${apiUrl}/api/patients`),
          fetch(`${apiUrl}/api/doctors`),
          fetch(`${apiUrl}/api/stats`)
        ])

        if (patientsRes.ok && doctorsRes.ok && statsRes.ok) {
          const [patientsData, doctorsData, statsData] = await Promise.all([
            patientsRes.json(),
            doctorsRes.json(),
            statsRes.json()
          ])
          setPatients(patientsData)
          setDoctors(doctorsData)
          setStats(statsData)
        } else {
          console.warn('API not available, using fallback data')
          setError('Using demo data')
        }
      } catch (err) {
        console.warn('Failed to fetch from API:', err)
        setError('Using demo data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

    // Poll for updates every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const canBook = selectedPatient && selectedDoctor

  const handleBook = async () => {
    if (!canBook) return

    setBookingStatus('Booking...')
    try {
      const apiUrl = `${window.location.protocol}//${window.location.hostname}:8000`
      const response = await fetch(`${apiUrl}/api/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: selectedPatient,
          doctor_id: selectedDoctor,
        }),
      })

      const result = await response.json()

      if (result.success) {
        setBookingStatus(`✅ Booked: ${result.appointment_id}`)
        // Refresh data after booking
        setTimeout(() => {
          setSelectedPatient(null)
          setSelectedDoctor(null)
          setBookingStatus(null)
          // Trigger data refresh
          window.location.reload()
        }, 2000)
      } else {
        setBookingStatus(`❌ ${result.message}`)
      }
    } catch (err) {
      setBookingStatus('❌ Booking failed')
    }
  }

  const handleChatMessage = async (message: string) => {
    if (!message.trim()) return

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: message.trim(),
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, userMessage])
    
    setIsProcessing(true)
    try {
      const apiUrl = `${window.location.protocol}//${window.location.hostname}:8000`
      const response = await fetch(`${apiUrl}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim(),
          session_id: chatSessionId
        }),
      })

      const result = await response.json()
      
      if (!chatSessionId && result.session_id) {
        setChatSessionId(result.session_id)
      }

      // Add assistant response to chat
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: result.message || "I've processed your message. How can I help you further?",
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, assistantMessage])

      // Refresh dashboard data after chat interaction
      const [patientsRes, statsRes] = await Promise.all([
        fetch(`${apiUrl}/api/patients`),
        fetch(`${apiUrl}/api/stats`)
      ])
      
      if (patientsRes.ok && statsRes.ok) {
        const patientsData = await patientsRes.json()
        const statsData = await statsRes.json()
        setPatients(patientsData)
        setStats(statsData)
      }
    } catch (err) {
      console.error('Chat message failed:', err)
      // Add error message to chat
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
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
          Healthcare Coordination Visualization {error && <span style={{ color: '#f59e0b' }}>({error})</span>}
        </p>
      </div>

      {/* Stats - responsive grid */}
      <div style={{
        position: 'absolute',
        top: '24px',
        right: '24px',
        display: 'grid',
        gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)',
        gap: isMobile ? '8px' : '24px',
        pointerEvents: 'auto',
        maxWidth: 'calc(100vw - 48px)'
      }}>
        <StatCard label='Active' value={stats.active_patients.toString()} color='#4a9eff' isMobile={isMobile} />
        <StatCard label='Reasoning' value={stats.in_reasoning.toString()} color='#8b5cf6' isMobile={isMobile} />
        {!isMobile && <StatCard label='Doctors' value={stats.available_doctors.toString()} color='#10b981' isMobile={isMobile} />}
      </div>

      {/* Control Panel - responsive width and position */}
      <div style={{
        position: 'absolute',
        bottom: isMobile ? '140px' : '24px',
        left: isMobile ? '16px' : '24px',
        right: isMobile ? '16px' : undefined,
        width: isMobile ? 'calc(100vw - 32px)' : '320px',
        maxWidth: '400px',
        background: 'rgba(10, 10, 26, 0.9)',
        borderRadius: isMobile ? '20px' : '16px',
        border: '1px solid rgba(74, 158, 255, 0.2)',
        backdropFilter: 'blur(10px)',
        pointerEvents: 'auto',
        overflow: 'hidden',
        zIndex: 999
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
            ? patients.map(patient => (
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
                      {STATUS_LABELS[patient.status] || patient.status}
                    </div>
                  </div>
                  <SeverityBadge severity={patient.severity} />
                </div>
              ))
            : doctors.map(doctor => (
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
            disabled={!canBook || bookingStatus !== null}
            style={{
              width: '100%',
              padding: '12px',
              background: canBook && !bookingStatus
                ? 'linear-gradient(135deg, #10b981, #059669)'
                : '#333',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 600,
              cursor: canBook && !bookingStatus ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s ease'
            }}
          >
            {bookingStatus || (canBook ? 'Confirm Booking' : 'Select Patient & Doctor')}
          </button>
        </div>
      </div>

      {/* Instructions - hide on mobile */}
      {!isMobile && (
        <div style={{
          position: 'absolute',
          bottom: '24px',
          right: showChat ? '420px' : '24px',
          fontSize: '11px',
          color: '#444',
          textAlign: 'right',
          pointerEvents: 'none',
          transition: 'right 0.3s ease'
        }}>
          <p style={{ margin: '0 0 4px 0' }}>🖱️ Click nodes to select</p>
          <p style={{ margin: 0 }}>🔄 Scene auto-rotates</p>
        </div>
      )}

      {/* Chat Toggle Button - responsive position */}
      <button
        onClick={() => setShowChat(!showChat)}
        style={{
          position: 'absolute',
          right: isMobile ? '16px' : '24px',
          bottom: isMobile ? '24px' : '24px',
          width: isMobile ? '56px' : '48px',
          height: isMobile ? '56px' : '48px',
          background: showChat 
            ? 'linear-gradient(135deg, #10b981, #059669)' 
            : 'linear-gradient(135deg, #4a9eff, #6366f1)',
          border: 'none',
          borderRadius: '50%',
          color: '#fff',
          fontSize: isMobile ? '24px' : '20px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(74, 158, 255, 0.3)',
          pointerEvents: 'auto',
          zIndex: 1001
        }}
      >
        💬
      </button>

      {/* Chat Panel */}
      {showChat && (
        <ChatPanel
          messages={chatMessages}
          onSendMessage={handleChatMessage}
          isProcessing={isProcessing}
        />
      )}
    </div>
  )
}

function StatCard({ label, value, color, isMobile }: { label: string; value: string; color: string; isMobile: boolean }) {
  return (
    <div style={{
      background: 'rgba(10, 10, 26, 0.8)',
      borderRadius: '12px',
      padding: isMobile ? '8px 12px' : '12px 20px',
      border: `1px solid ${color}33`,
      textAlign: 'center',
      minWidth: isMobile ? '60px' : 'auto'
    }}>
      <div style={{ fontSize: isMobile ? '18px' : '24px', fontWeight: 700, color }}>
        {value}
      </div>
      <div style={{ fontSize: isMobile ? '8px' : '10px', color: '#666', textTransform: 'uppercase' }}>
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
      background: `${colors[severity] || '#666'}22`,
      color: colors[severity] || '#666',
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
