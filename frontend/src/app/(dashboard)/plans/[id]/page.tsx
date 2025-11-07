'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  ArrowLeft,
  Download,
  Edit,
  Share2,
  FileText,
  Home,
  Ruler,
  Layers,
  Clock,
  CheckCircle,
  XCircle,
  Loader,
  Eye,
  MoreHorizontal,
  Trash2,
  RefreshCw
} from 'lucide-react'
import { Plan, PlanStatus } from '@/types'
import { apiClient } from '@/lib/api'
import DXFViewer from '@/components/cad/DXFViewer'
import { usePlanWebSocket, useStepName } from '@/hooks/useWebSocket'
import PlanErrorHandler, { createWebSocketError } from '@/components/ui/ErrorHandler'

// Mock data for development - now replaced with real API calls

export default function PlanDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [plan, setPlan] = useState<Plan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  
  // WebSocket integration for real-time updates
  const {
    isConnected,
    status: wsStatus,
    progress: wsProgress,
    currentStep,
    message: wsMessage,
    error: wsError,
    aiUpdate,
    connectionError,
    reconnect
  } = usePlanWebSocket(params.id as string)
  
  const stepName = useStepName(currentStep)

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Get all plans and find the specific one
        // TODO: Backend should have a dedicated endpoint for getting a single plan
        const response = await apiClient.listPlans()
        
        if (response.success && response.data) {
          const foundPlan = response.data.find(p => p.id === params.id)
          if (foundPlan) {
            setPlan(foundPlan)
          } else {
            setError('Plan not found')
          }
        }
      } catch (err) {
        console.error('Failed to fetch plan:', err)
        setError('Failed to load plan. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    if (params.id) {
      fetchPlan()
    }
  }, [params.id])
  
  // Update plan status from WebSocket
  useEffect(() => {
    if (wsStatus && plan) {
      setPlan(prev => prev ? { ...prev, status: wsStatus, progress: wsProgress } : null)
    }
  }, [wsStatus, wsProgress, plan])

  const getStatusColor = (status: PlanStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'generating':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
      case 'initializing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300'
      default:
        return 'bg-muted text-foreground dark:bg-muted/50'
    }
  }

  const getStatusIcon = (status: PlanStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'generating':
        return <Loader className="w-4 h-4 animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      case 'initializing':
        return <Clock className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  const getStatusText = (status: PlanStatus) => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'generating':
        return 'Generating...'
      case 'failed':
        return 'Failed'
      case 'initializing':
        return 'Initializing...'
      default:
        return status
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const handleDownload = async () => {
    if (!plan) return
    
    setIsDownloading(true)
    try {
      const response = await fetch(`/api/v1/plans/${plan.id}/download`)
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`)
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${plan.name}.dxf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log('Successfully downloaded DXF file:', plan.name)
    } catch (error) {
      console.error('Download failed:', error)
      // You might want to show an error toast here
    } finally {
      setIsDownloading(false)
    }
  }

  const handleRegenerate = async () => {
    if (!plan) return
    
    setIsRegenerating(true)
    try {
      // await apiClient.regeneratePlan(plan.id)
      console.log('Regenerating plan:', plan.id)
      
      // Simulate regeneration
      setTimeout(() => {
        setIsRegenerating(false)
        // Update plan status
        setPlan({
          ...plan,
          status: 'generating',
          progress: 0
        })
      }, 1000)
    } catch (error) {
      console.error('Regeneration failed:', error)
      setIsRegenerating(false)
    }
  }

  const handleDelete = async () => {
    if (!plan) return
    
    if (confirm('Are you sure you want to delete this plan? This action cannot be undone.')) {
      try {
        // await apiClient.deletePlan(plan.id)
        console.log('Deleting plan:', plan.id)
        router.push('/plans')
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/3"></div>
            <div className="h-64 bg-muted rounded"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="h-48 bg-muted rounded"></div>
              <div className="h-48 bg-muted rounded"></div>
              <div className="h-48 bg-muted rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="p-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">Plan Not Found</h1>
          <p className="text-muted-foreground mb-6">The plan you're looking for doesn't exist or has been deleted.</p>
          <Button onClick={() => router.push('/plans')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Plans
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => router.push('/plans')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Plans
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground">{plan.name}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <Badge className={getStatusColor(plan.status)}>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(plan.status)}
                    <span>{getStatusText(plan.status)}</span>
                  </div>
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Created {formatDate(plan.created_at)}
                </span>
                <span className="text-sm text-muted-foreground">
                  Updated {formatDate(plan.updated_at)}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button 
              onClick={handleDownload}
              disabled={isDownloading || plan.status !== 'completed'}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>{isDownloading ? 'Downloading...' : 'Download'}</span>
            </Button>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Progress Bar with WebSocket Updates */}
        {(plan.status === 'generating' || wsStatus === 'generating') && (
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">
                  {stepName || 'Generation Progress'}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-muted-foreground">
                    {wsProgress || plan.progress}%
                  </span>
                  {isConnected ? (
                    <Badge variant="outline" className="text-xs">
                      Live
                    </Badge>
                  ) : connectionError ? (
                    <Badge variant="outline" className="text-xs text-orange-500">
                      Reconnecting...
                    </Badge>
                  ) : null}
                </div>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${wsProgress || plan.progress}%` }}
                />
              </div>
              {(wsMessage || plan.status === 'generating') && (
                <p className="text-sm text-muted-foreground mt-2">
                  {wsMessage || 'Your floor plan is being generated. This typically takes 2-5 minutes.'}
                </p>
              )}
              
              {/* AI Update Indicator */}
              {aiUpdate && (
                <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-950/20 rounded border">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                      AI Enhancement Active
                    </span>
                  </div>
                  {aiUpdate.analysis_completed && (
                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                      Requirements analysis completed
                    </p>
                  )}
                  {aiUpdate.optimizations_applied && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                      {aiUpdate.applied_count} optimizations applied
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* WebSocket Connection Error */}
        {connectionError && (
          <PlanErrorHandler
            error={createWebSocketError(connectionError)}
            onRetry={reconnect}
            onDismiss={() => setError(null)}
            compact
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Plan Viewer */}
          <div className="lg:col-span-2 space-y-6">
            {/* CAD Viewer */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="w-5 h-5" />
                  <span>Floor Plan View</span>
                </CardTitle>
                <CardDescription>
                  Interactive 2D view of your generated floor plan
                </CardDescription>
              </CardHeader>
              <CardContent>
                {plan.status === 'completed' ? (
                  <DXFViewer 
                    planId={plan.id}
                    onLoad={() => console.log('DXF viewer loaded successfully')}
                    onError={(error) => console.error('DXF viewer error:', error)}
                  />
                ) : (
                  <div className="bg-muted rounded-lg h-96 flex items-center justify-center">
                    <div className="text-center">
                      <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-foreground mb-2">Floor Plan View</h3>
                      <p className="text-muted-foreground mb-4">
                        Floor plan view will be available once generation is complete
                      </p>
                      <Badge variant="outline">
                        {getStatusText(plan.status)}
                      </Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Room Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Home className="w-5 h-5" />
                  <span>Room Details</span>
                </CardTitle>
                <CardDescription>
                  Breakdown of all rooms in your floor plan
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {plan.rooms?.map((room, index) => (
                    <div key={room.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <span className="text-lg font-medium text-blue-600">{index + 1}</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-foreground">{room.name}</h4>
                          <p className="text-sm text-muted-foreground capitalize">{room.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-foreground">{room.area}m²</p>
                        <p className="text-sm text-muted-foreground">
                          {((room.area / (plan.summary?.building_area || 1)) * 100).toFixed(1)}% of total
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Plan Info & Actions */}
          <div className="space-y-6">
            {/* Plan Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Layers className="w-5 h-5" />
                  <span>Plan Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground">Building Type</label>
                  <p className="text-foreground capitalize">{plan.building_type}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">Dimensions</label>
                  <p className="text-foreground">{plan.dimensions.width}m × {plan.dimensions.height}m</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">Total Area</label>
                  <p className="text-foreground">{plan.summary?.building_area || 0}m²</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">Total Rooms</label>
                  <p className="text-foreground">{plan.summary?.total_rooms || 0}</p>
                </div>
                {plan.summary?.efficiency_score && (
                  <div>
                    <label className="text-sm font-medium text-foreground">Efficiency Score</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-muted rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${plan.summary.efficiency_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{plan.summary.efficiency_score}%</span>
                    </div>
                  </div>
                )}
                
                {/* AI Enhancement Indicator */}
                {plan.summary?.ai_enhanced && (
                  <div>
                    <label className="text-sm font-medium text-foreground">AIEnhancement</label>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="secondary" className="text-xs">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
                        AI Enhanced
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        Powered by AI analysis
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* File Information */}
            {plan.status === 'completed' && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="w-5 h-5" />
                    <span>File Information</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-foreground">File Format</label>
                    <p className="text-foreground">DXF (Drawing Exchange Format)</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground">File Size</label>
                    <p className="text-foreground">{formatFileSize(plan.summary?.file_size || 0)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground">Compatibility</label>
                    <p className="text-foreground">AutoCAD, Revit, SketchUp, etc.</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full"
                  onClick={handleDownload}
                  disabled={isDownloading || plan.status !== 'completed'}
                >
                  <Download className="w-4 h-4 mr-2" />
                  {isDownloading ? 'Downloading...' : 'Download DXF'}
                </Button>
                <Button variant="outline" className="w-full">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share Plan
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleRegenerate}
                  disabled={isRegenerating}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
                  {isRegenerating ? 'Regenerating...' : 'Regenerate'}
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => router.push(`/plans/${plan.id}/edit`)}
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Plan
                </Button>
                <Button 
                  variant="ghost" 
                  className="w-full text-red-500 hover:text-red-700"
                  onClick={handleDelete}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Plan
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}