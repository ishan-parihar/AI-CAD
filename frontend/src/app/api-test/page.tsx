'use client'

import React, { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'

export default function ApiTest() {
  const [status, setStatus] = useState<string>('Loading...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await apiClient.healthCheck()
        setStatus(`✅ Connected: ${response.message}`)
      } catch (err) {
        setError(`❌ Connection failed: ${err}`)
      }
    }

    testConnection()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">API Connection Test</h1>
        <div className="space-y-4">
          <div className="p-4 bg-gray-100 rounded">
            <p className="text-sm font-mono">{status}</p>
          </div>
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
          <div className="text-xs text-gray-500">
            <p>Frontend: http://localhost:3001</p>
            <p>Backend: http://localhost:8100</p>
          </div>
        </div>
      </div>
    </div>
  )
}