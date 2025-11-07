'use client'

import { useState } from 'react'
import { useAIConfig } from '@/hooks/useAIConfig'

export default function AIConfigPanel() {
  const { config, isLoading, error, updateConfig, testConnection, loadConfig } = useAIConfig()
  const [formData, setFormData] = useState({
    baseUrl: config.baseUrl || '',
    apiKey: config.apiKey || '',
    modelName: config.modelName || '',
    enabled: config.enabled || false
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSave = async () => {
    const result = await updateConfig(formData)
    if (result.success) {
      // Show success message
      alert('AI configuration saved successfully!')
    } else {
      // Show error message
      alert(`Error: ${result.message}`)
    }
  }

  const handleTest = async () => {
    const result = await testConnection()
    if (result.success) {
      alert('AI connection test successful!')
    } else {
      alert(`Connection test failed: ${result.message}`)
    }
  }

  const loadDefaultConfigs = () => {
    // Pre-configured options for common providers
    const presets = {
      'OpenAI': {
        baseUrl: 'https://api.openai.com/v1',
        modelName: 'gpt-4'
      },
      'Anthropic Claude': {
        baseUrl: 'https://api.anthropic.com',
        modelName: 'claude-3-sonnet-20240229'
      },
      'Local Ollama': {
        baseUrl: 'http://localhost:11434/v1',
        modelName: 'llama2'
      },
      'Custom': {
        baseUrl: '',
        modelName: ''
      }
    }

    const selectedPreset = presets['OpenAI'] // Default to OpenAI
    setFormData(prev => ({
      ...prev,
      ...selectedPreset
    }))
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">AI Configuration</h2>
        <button
          onClick={loadDefaultConfigs}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
        >
          Load OpenAI Defaults
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Base URL
          </label>
          <input
            type="url"
            name="baseUrl"
            value={formData.baseUrl}
            onChange={handleInputChange}
            placeholder="https://api.openai.com/v1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            OpenAI-compatible API endpoint URL
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key
          </label>
          <input
            type="password"
            name="apiKey"
            value={formData.apiKey}
            onChange={handleInputChange}
            placeholder="sk-..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Your API key for the OpenAI-compatible service
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Model Name
          </label>
          <input
            type="text"
            name="modelName"
            value={formData.modelName}
            onChange={handleInputChange}
            placeholder="gpt-4"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            The model name to use for generation
          </p>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            name="enabled"
            id="enabled"
            checked={formData.enabled}
            onChange={handleInputChange}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="enabled" className="ml-2 block text-sm text-gray-900">
            Enable AI features
          </label>
        </div>
      </div>

      <div className="mt-6 flex space-x-4">
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Configuration'}
        </button>
        
        <button
          onClick={handleTest}
          disabled={isLoading || !formData.baseUrl || !formData.apiKey}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Testing...' : 'Test Connection'}
        </button>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Quick Setup Guide</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• <strong>OpenAI:</strong> Use https://api.openai.com/v1 and your OpenAI API key</li>
          <li>• <strong>Local Models:</strong> Use http://localhost:11434/v1 for Ollama</li>
          <li>• <strong>Other Providers:</strong> Use the provider's API endpoint URL</li>
          <li>• Make sure the model name matches what's available on your chosen service</li>
        </ul>
      </div>
    </div>
  )
}