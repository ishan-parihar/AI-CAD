'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { PlanStatus } from '@/types'

interface WebSocketMessage {
  type: string
  plan_id: string
  timestamp?: number
  [key: string]: any
}

interface PlanUpdate {
  status: PlanStatus
  progress: number
  current_step?: string
  message?: string
  error?: string
}

interface AIUpdate {
  analysis_completed?: boolean
  insights?: string[]
  recommendations?: string[]
  optimizations_completed?: boolean
  suggestions?: Array<{
    description: string
    confidence: number
  }>
  confidence_score?: number
  optimizations_applied?: boolean
  applied_count?: number
  applied_optimizations?: string[]
}

interface UseWebSocketReturn {
  isConnected: boolean
  status: PlanStatus | null
  progress: number
  currentStep: string | null
  message: string | null
  error: string | null
  aiUpdate: AIUpdate | null
  connectionError: string | null
  sendMessage: (message: any) => void
  reconnect: () => void
}

export function usePlanWebSocket(planId: string): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [status, setStatus] = useState<PlanStatus | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [aiUpdate, setAiUpdate] = useState<AIUpdate | null>(null)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  
  const websocketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5
  
  const connect = useCallback(() => {
    if (!planId) return
    
    try {
      // Determine WebSocket URL based on current environment
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'
      const wsHost = apiBaseUrl.replace(/^https?:\/\//, '')
      const wsUrl = `${wsProtocol}//${wsHost}/ws/plans/${planId}`
      
      console.log(`Attempting WebSocket connection to: ${wsUrl}`)
      
      websocketRef.current = new WebSocket(wsUrl)
      
      websocketRef.current.onopen = () => {
        console.log(`WebSocket connected for plan ${planId}`)
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttemptsRef.current = 0
        
        // Send subscription message
        websocketRef.current?.send(JSON.stringify({
          type: 'subscribe_updates'
        }))
      }
      
      websocketRef.current.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)
          
          switch (data.type) {
            case 'connection_established':
              console.log('WebSocket connection established')
              break
              
            case 'initial_status':
              setStatus(data.status)
              setProgress(data.progress || 0)
              setMessage(data.message || null)
              setError(data.error || null)
              break
              
            case 'plan_update':
              const update = data as unknown as PlanUpdate
              setStatus(update.status)
              setProgress(update.progress || 0)
              setCurrentStep(update.current_step || null)
              setMessage(update.message || null)
              setError(update.error || null)
              break
              
            case 'ai_update':
              setAiUpdate(data as AIUpdate)
              break
              
            case 'layout_summary':
              // Handle layout specific updates
              console.log('Layout summary received:', data)
              break
              
            case 'error':
              setError(data.message || 'Unknown error occurred')
              console.error('WebSocket error:', data)
              break
              
            case 'pong':
              // Handle ping/pong for connection health
              break
              
            case 'plan_deleted':
              console.log('Plan was deleted')
              setError('Plan has been deleted')
              break
              
            case 'plan_not_found':
              setError('Plan not found')
              break
              
            default:
              console.log('Unknown WebSocket message type:', data.type, data)
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
      
      websocketRef.current.onclose = (event) => {
        console.log(`WebSocket disconnected for plan ${planId}, code: ${event.code}, reason: ${event.reason}`)
        console.log('WebSocket URL was:', wsUrl)
        setIsConnected(false)
        
        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000)
          console.log(`Attempting to reconnect in ${delay}ms...`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, delay)
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setConnectionError('Failed to establish WebSocket connection after multiple attempts')
        }
      }
      
      websocketRef.current.onerror = (event) => {
        console.error('WebSocket error:', event)
        console.error('WebSocket URL:', wsUrl)
        console.error('WebSocket readyState:', websocketRef.current?.readyState)
        
        // More detailed error information
        if (websocketRef.current?.readyState === WebSocket.CLOSED) {
          console.error('WebSocket closed - connection was terminated')
        }
        
        setConnectionError(`WebSocket connection error to ${wsUrl}`)
      }
      
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err)
      setConnectionError('Failed to create WebSocket connection')
    }
  }, [planId])
  
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (websocketRef.current) {
      websocketRef.current.close(1000, 'Component unmounting')
      websocketRef.current = null
    }
    
    setIsConnected(false)
  }, [])
  
  const sendMessage = useCallback((message: any) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message:', message)
    }
  }, [])
  
  const reconnect = useCallback(() => {
    disconnect()
    reconnectAttemptsRef.current = 0
    setConnectionError(null)
    setTimeout(connect, 100)
  }, [disconnect, connect])
  
  // Send periodic ping to keep connection alive
  useEffect(() => {
    if (!isConnected) return
    
    const pingInterval = setInterval(() => {
      sendMessage({ type: 'ping' })
    }, 30000) // Ping every 30 seconds
    
    return () => clearInterval(pingInterval)
  }, [isConnected, sendMessage])
  
  // Connect when component mounts or planId changes
  useEffect(() => {
    if (planId) {
      connect()
    }
    
    return () => {
      disconnect()
    }
  }, [planId, connect, disconnect])
  
  return {
    isConnected,
    status,
    progress,
    currentStep,
    message,
    error,
    aiUpdate,
    connectionError,
    sendMessage,
    reconnect
  }
}

// Helper hook for displaying human-readable step names
export function useStepName(step: string | null): string {
  const stepNames: Record<string, string> = {
    'ai_analysis': 'AI Requirements Analysis',
    'initializing_cad': 'Initializing CAD Components',
    'creating_boundaries': 'Creating Building Boundaries',
    'spatial_reasoning': 'Generating Room Layout',
    'layout_complete': 'Layout Generation Complete',
    'ai_optimization': 'AI Optimization',
    'adding_openings': 'Adding Doors and Windows',
    'validation': 'Design Rules Validation',
    'saving': 'Saving DXF File'
  }
  
  return step ? stepNames[step] || step : 'Initializing...'
}