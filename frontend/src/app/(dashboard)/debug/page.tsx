'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export default function WebSocketDebugPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [wsUrl, setWsUrl] = useState('ws://localhost:8100/ws/plans/test-plan-123')
  const [testPlanId, setTestPlanId] = useState('debug-test-plan')
  
  const addLog = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️'
    setLogs(prev => [...prev, `${timestamp} ${prefix} ${message}`])
  }

  const testWebSocketConnection = () => {
    addLog(`Testing WebSocket connection to: ${wsUrl}`)
    
    try {
      const websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        addLog('WebSocket connected successfully!', 'success')
        setIsConnected(true)
        setConnectionError(null)
        
        // Send subscription message
        websocket.send(JSON.stringify({
          type: 'subscribe_updates'
        }))
        addLog('Sent subscription message')
      }
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          addLog(`Received: ${data.type} - ${JSON.stringify(data).substring(0, 100)}...`)
        } catch (err) {
          addLog(`Received raw: ${event.data}`)
        }
      }
      
      websocket.onerror = (event) => {
        addLog(`WebSocket error: ${event}`, 'error')
        setConnectionError('WebSocket connection error')
      }
      
      websocket.onclose = (event) => {
        addLog(`WebSocket closed - Code: ${event.code}, Reason: ${event.reason}`)
        setIsConnected(false)
      }
      
      // Store reference for debugging
      (window as any).debugWebSocket = websocket
      
      // Close after 10 seconds for testing
      setTimeout(() => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.close(1000, 'Test complete')
          addLog('Test complete - closing connection')
        }
      }, 10000)
      
    } catch (error) {
      addLog(`Failed to create WebSocket: ${error}`, 'error')
      setConnectionError(`Failed to create WebSocket: ${error}`)
    }
  }
  
  const testBackendConnection = async () => {
    addLog('Testing backend HTTP connection...')
    
    try {
      const response = await fetch('http://localhost:8100/api/v1/health')
      if (response.ok) {
        const data = await response.json()
        addLog(`Backend health check passed: ${data.status}`, 'success')
      } else {
        addLog(`Backend health check failed: ${response.status}`, 'error')
      }
    } catch (error) {
      addLog(`Backend connection failed: ${error}`, 'error')
    }
  }
  
  const createTestPlan = async () => {
    addLog('Creating test plan...')
    
    try {
      const response = await fetch('http://localhost:8100/api/v1/plans/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'WebSocket Debug Test Plan',
          building_type: 'residential',
          dimensions: { width: 10, height: 8 },
          rooms: [
            { type: 'bedroom', area: 15 },
            { type: 'kitchen', area: 12 }
          ],
          constraints: {}
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        const planId = data.plan_id
        addLog(`Test plan created: ${planId}`, 'success')
        setTestPlanId(planId)
        setWsUrl(`ws://localhost:8100/ws/plans/${planId}`)
      } else {
        addLog(`Failed to create plan: ${response.status}`, 'error')
      }
    } catch (error) {
      addLog(`Plan creation failed: ${error}`, 'error')
    }
  }
  
  const clearLogs = () => {
    setLogs([])
  }
  
  useEffect(() => {
    addLog('WebSocket Debug Tool initialized')
    addLog(`Current WebSocket URL: ${wsUrl}`)
    
    // Auto-test backend connection
    testBackendConnection()
  }, [])
  
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground">WebSocket Connection Debug</h1>
          <p className="text-muted-foreground">Debug WebSocket connection issues between frontend and backend</p>
        </div>

        {/* Connection Status */}
        <Card>
          <CardHeader>
            <CardTitle>Connection Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Badge variant={isConnected ? "default" : "secondary"}>
                  {isConnected ? 'Connected' : 'Disconnected'}
                </Badge>
                {connectionError && (
                  <Badge variant="destructive">
                    Error: {connectionError}
                  </Badge>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  WebSocket URL
                </label>
                <input
                  type="text"
                  value={wsUrl}
                  onChange={(e) => setWsUrl(e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-md"
                  placeholder="ws://localhost:8100/ws/plans/plan-id"
                />
              </div>
              
              <div className="flex space-x-2">
                <Button onClick={testWebSocketConnection}>
                  Test WebSocket
                </Button>
                <Button variant="outline" onClick={testBackendConnection}>
                  Test Backend
                </Button>
                <Button variant="outline" onClick={createTestPlan}>
                  Create Test Plan
                </Button>
                <Button variant="outline" onClick={clearLogs}>
                  Clear Logs
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Debug Logs */}
        <Card>
          <CardHeader>
            <CardTitle>Debug Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted rounded-lg p-4 h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-muted-foreground">No logs yet. Click "Test WebSocket" to start debugging.</p>
              ) : (
                <div className="space-y-1 font-mono text-sm">
                  {logs.map((log, index) => (
                    <div key={index} className="text-foreground">
                      {log}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Manual Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Manual Testing Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p>1. Ensure the backend is running on port 8100</p>
              <p>2. Open browser developer tools (F12)</p>
              <p>3. Go to Console tab</p>
              <p>4. Run this code to test WebSocket manually:</p>
              <div className="bg-muted p-3 rounded font-mono text-xs">
{`const ws = new WebSocket('${wsUrl}');
ws.onopen = () => console.log('WebSocket opened');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.onerror = (e) => console.error('WebSocket error:', e);
ws.onclose = (e) => console.log('WebSocket closed:', e);`}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}