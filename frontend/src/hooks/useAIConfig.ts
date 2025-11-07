'use client'

import { useState } from 'react'

interface AIConfig {
  baseUrl: string
  apiKey: string
  modelName: string
  enabled: boolean
}

interface AIConfigResponse {
  success: boolean
  message: string
  config?: AIConfig
}

export function useAIConfig() {
  const [config, setConfig] = useState<AIConfig>({
    baseUrl: '',
    apiKey: '',
    modelName: '',
    enabled: false
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateConfig = async (newConfig: Partial<AIConfig>): Promise<AIConfigResponse> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/v1/settings/ai-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig),
      })
      
      const result = await response.json()
      
      if (response.ok) {
        setConfig(prev => ({ ...prev, ...newConfig }))
        return { success: true, message: 'AI configuration updated successfully' }
      } else {
        const errorMessage = result.message || 'Failed to update AI configuration'
        setError(errorMessage)
        return { success: false, message: errorMessage }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error'
      setError(errorMessage)
      return { success: false, message: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }

  const testConnection = async (): Promise<AIConfigResponse> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/v1/settings/test-ai-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const result = await response.json()
      
      if (response.ok) {
        return { success: true, message: 'AI connection test successful' }
      } else {
        const errorMessage = result.message || 'AI connection test failed'
        setError(errorMessage)
        return { success: false, message: errorMessage }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error'
      setError(errorMessage)
      return { success: false, message: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }

  const loadConfig = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/v1/settings/ai-config')
      const result = await response.json()
      
      if (response.ok && result.config) {
        setConfig(result.config)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load AI configuration'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    config,
    isLoading,
    error,
    updateConfig,
    testConnection,
    loadConfig
  }
}