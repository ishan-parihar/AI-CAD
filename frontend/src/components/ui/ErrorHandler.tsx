'use client'

import React from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  AlertCircle, 
  RefreshCw, 
  Lightbulb, 
  ExternalLink,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react'

export interface PlanError {
  code: string
  message: string
  details?: string
  suggestions?: string[]
  type: 'warning' | 'error' | 'info'
  retryable?: boolean
  documentation_url?: string
}

interface PlanErrorHandlerProps {
  error: PlanError | string | null
  onRetry?: () => void
  onDismiss?: () => void
  className?: string
  showRetry?: boolean
  compact?: boolean
}

const ERROR_CATEGORIES = {
  'INSUFFICIENT_SPACE': {
    icon: <AlertCircle className="w-4 h-4" />,
    title: 'Space Constraint Issue',
    suggestions: [
      'Try reducing room sizes',
      'Remove optional rooms',
      'Increase building dimensions',
      'Consider open-concept layout'
    ],
    retryable: true,
    type: 'warning' as const
  },
  'INVALID_LAYOUT': {
    icon: <XCircle className="w-4 h-4" />,
    title: 'Layout Configuration Error',
    suggestions: [
      'Adjust room relationships',
      'Check dimension constraints',
      'Review adjacency requirements',
      'Simplify room configuration'
    ],
    retryable: true,
    type: 'error' as const
  },
  'AI_SERVICE_UNAVAILABLE': {
    icon: <Clock className="w-4 h-4" />,
    title: 'AI Service Temporarily Unavailable',
    suggestions: [
      'Using algorithmic layout generation',
      'AI features will be available later',
      'Your plan will still be generated successfully',
      'Try again later for AI enhancements'
    ],
    retryable: false,
    type: 'info' as const
  },
  'GENERATION_FAILED': {
    icon: <XCircle className="w-4 h-4" />,
    title: 'Plan Generation Failed',
    suggestions: [
      'Check your internet connection',
      'Try with simpler requirements',
      'Contact support if issue persists',
      'Try refreshing the page'
    ],
    retryable: true,
    type: 'error' as const
  },
  'WEBSOCKET_CONNECTION_FAILED': {
    icon: <AlertCircle className="w-4 h-4" />,
    title: 'Real-time Updates Unavailable',
    suggestions: [
      'Manual refresh may be needed',
      'Check your internet connection',
      'Some features may be limited',
      'Try refreshing the page'
    ],
    retryable: true,
    type: 'warning' as const
  },
  'DXF_PARSE_ERROR': {
    icon: <XCircle className="w-4 h-4" />,
    title: 'DXF File Error',
    suggestions: [
      'Regenerate the plan',
      'Try different layout configuration',
      'Contact support if issue persists',
      'File may be corrupted'
    ],
    retryable: true,
    type: 'error' as const
  }
}

export default function PlanErrorHandler({ 
  error, 
  onRetry, 
  onDismiss, 
  className = '',
  showRetry = true,
  compact = false 
}: PlanErrorHandlerProps) {
  if (!error) return null

  // Handle string errors
  let errorObj: PlanError
  if (typeof error === 'string') {
    errorObj = {
      code: 'UNKNOWN_ERROR',
      message: error,
      type: 'error'
    }
  } else {
    errorObj = error
  }

  const category = ERROR_CATEGORIES[errorObj.code as keyof typeof ERROR_CATEGORIES]
  const suggestions = errorObj.suggestions || category?.suggestions || []
  const isRetryable = errorObj.retryable ?? category?.retryable ?? false
  const errorType = errorObj.type || category?.type || 'error'

  const getAlertVariant = (type: string) => {
    switch (type) {
      case 'warning': return 'default'
      case 'info': return 'default'
      case 'error': return 'destructive'
      default: return 'destructive'
    }
  }

  const getStatusIcon = (type: string) => {
    switch (type) {
      case 'warning': return <AlertCircle className="w-4 h-4" />
      case 'info': return <Lightbulb className="w-4 h-4" />
      case 'error': return <XCircle className="w-4 h-4" />
      default: return <XCircle className="w-4 h-4" />
    }
  }

  if (compact) {
    return (
      <Alert variant={getAlertVariant(errorType)} className={className}>
        <div className="flex items-center">
          {getStatusIcon(errorType)}
        </div>
        <AlertDescription className="flex items-center justify-between">
          <span className="truncate">{errorObj.message}</span>
          {showRetry && isRetryable && onRetry && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRetry}
              className="ml-2 flex-shrink-0"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Retry
            </Button>
          )}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Alert variant={getAlertVariant(errorType)}>
        {category?.icon || getStatusIcon(errorType)}
        <div className="flex-1">
          <AlertTitle className="flex items-center justify-between">
            <span>{category?.title || 'Error'}</span>
            <Badge variant="outline" className="text-xs">
              {errorObj.code}
            </Badge>
          </AlertTitle>
          <AlertDescription className="mt-2">
            {errorObj.message}
            {errorObj.details && (
              <details className="mt-2">
                <summary className="cursor-pointer text-sm opacity-75 hover:opacity-100">
                  Technical Details
                </summary>
                <pre className="mt-2 text-xs bg-muted p-2 rounded overflow-auto">
                  {errorObj.details}
                </pre>
              </details>
            )}
          </AlertDescription>
        </div>
        {onDismiss && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onDismiss}
            className="ml-2"
          >
            ×
          </Button>
        )}
      </Alert>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Alert variant="default">
          <Lightbulb className="w-4 h-4" />
          <AlertTitle>Suggested Solutions</AlertTitle>
          <AlertDescription>
            <ul className="mt-2 space-y-1 text-sm">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {showRetry && isRetryable && onRetry && (
            <Button onClick={onRetry} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          )}
          
          {errorObj.documentation_url && (
            <Button variant="outline" asChild>
              <a 
                href={errorObj.documentation_url} 
                target="_blank" 
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Documentation
              </a>
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
          {errorType === 'warning' && (
            <span className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              This is a warning, you can continue
            </span>
          )}
          {errorType === 'info' && (
            <span className="flex items-center">
              <Lightbulb className="w-3 h-3 mr-1" />
              Informational message
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// Specific error creators
export const createSpaceError = (details?: string): PlanError => ({
  code: 'INSUFFICIENT_SPACE',
  message: 'The requested layout doesn\'t fit within the specified dimensions.',
  details,
  type: 'warning'
})

export const createLayoutError = (details?: string): PlanError => ({
  code: 'INVALID_LAYOUT',
  message: 'The room configuration is invalid or conflicts with design rules.',
  details,
  type: 'error'
})

export const createAIServiceError = (details?: string): PlanError => ({
  code: 'AI_SERVICE_UNAVAILABLE',
  message: 'AI services are temporarily unavailable. Using algorithmic generation.',
  details,
  type: 'info'
})

export const createGenerationError = (details?: string): PlanError => ({
  code: 'GENERATION_FAILED',
  message: 'Plan generation failed due to an unexpected error.',
  details,
  type: 'error'
})

export const createWebSocketError = (details?: string): PlanError => ({
  code: 'WEBSOCKET_CONNECTION_FAILED',
  message: 'Real-time updates are unavailable. Manual refresh may be needed.',
  details,
  type: 'warning'
})

export const createDXFParseError = (details?: string): PlanError => ({
  code: 'DXF_PARSE_ERROR',
  message: 'Failed to parse or display the DXF file.',
  details,
  type: 'error'
})