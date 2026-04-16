'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatPanelProps {
  messages: Message[]
  onSendMessage: (message: string) => Promise<void>
  isProcessing: boolean
}

export default function ChatPanel({ messages, onSendMessage, isProcessing }: ChatPanelProps) {
  const [input, setInput] = useState('')
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 1200
  )
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Responsive dimensions
  const isMobile = windowWidth < 768
  const panelWidth = isMobile ? '90vw' : '380px'
  const panelHeight = isMobile ? '60vh' : '500px'
  const panelRight = isMobile ? '5vw' : '24px'
  const panelBottom = isMobile ? '80px' : '100px'

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return
    const message = input.trim()
    setInput('')
    try {
      await onSendMessage(message)
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{
      position: 'absolute',
      right: panelRight,
      bottom: panelBottom,
      width: panelWidth,
      maxWidth: '400px',
      height: panelHeight,
      maxHeight: isMobile ? '70vh' : '500px',
      background: 'rgba(10, 10, 26, 0.95)',
      borderRadius: isMobile ? '20px' : '16px',
      border: '1px solid rgba(74, 158, 255, 0.3)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      backdropFilter: 'blur(10px)',
      zIndex: 1000
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        background: 'rgba(74, 158, 255, 0.1)'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '16px',
          color: '#4a9eff'
        }}>
          💬 DocSync Chat
        </h3>
        <p style={{
          margin: '4px 0 0 0',
          fontSize: '11px',
          color: '#666'
        }}>
          Describe your symptoms to get started
        </p>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            <div style={{
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: msg.role === 'user' 
                ? '16px 16px 4px 16px'
                : '16px 16px 16px 4px',
              background: msg.role === 'user'
                ? 'linear-gradient(135deg, #4a9eff, #6366f1)'
                : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontSize: '14px',
              lineHeight: 1.5,
              whiteSpace: 'pre-wrap'
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '16px 16px 16px 4px',
              background: 'rgba(255,255,255,0.05)',
              color: '#888',
              fontSize: '14px'
            }}>
              Processing your request...
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        gap: '12px'
      }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Describe your symptoms..."
          disabled={isProcessing}
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            padding: '12px',
            color: '#fff',
            fontSize: '14px',
            resize: 'none',
            minHeight: '44px',
            maxHeight: '100px',
            fontFamily: 'inherit'
          }}
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isProcessing}
          style={{
            padding: '12px 20px',
            background: input.trim() && !isProcessing
              ? 'linear-gradient(135deg, #4a9eff, #6366f1)'
              : '#333',
            border: 'none',
            borderRadius: '12px',
            color: '#fff',
            fontSize: '14px',
            fontWeight: 600,
            cursor: input.trim() && !isProcessing ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s ease'
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}
