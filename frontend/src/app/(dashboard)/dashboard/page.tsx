'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  Plus, 
  FileText, 
  Download, 
  Clock, 
  TrendingUp,
  Users,
  Activity,
  ArrowRight,
  MoreHorizontal
} from 'lucide-react'
import { Plan, PlanStatus } from '@/types'
import { apiClient } from '@/lib/api'

// Mock data for development - now replaced with real API calls

export default function DashboardPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState({
    totalPlans: 0,
    completedPlans: 0,
    generatingPlans: 0,
    totalArea: 0
  })
  const [error, setError] = useState<string | null>(null)
  const [downloadingPlan, setDownloadingPlan] = useState<string | null>(null)

  // Fetch real data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Fetch plans only - stats endpoint doesn't exist in backend yet
        const plansResponse = await apiClient.listPlans({}, { field: 'updated_at', direction: 'desc' }, 1, 20)
        
        if (plansResponse.success && plansResponse.data) {
          setPlans(plansResponse.data.slice(0, 5)) // Show only 5 recent plans
          
          // Calculate stats from plans data
          const plans = plansResponse.data
          const completedPlans = plans.filter(p => p.status === 'completed').length
          const generatingPlans = plans.filter(p => p.status === 'generating' || p.status === 'initializing').length
          const totalArea = plans.reduce((sum, p) => {
            const area = (p.dimensions?.width || 0) * (p.dimensions?.height || 0)
            return sum + area
          }, 0)
          
          setStats({
            totalPlans: plans.length,
            completedPlans,
            generatingPlans,
            totalArea: Math.round(totalArea * 10) / 10 // Round to 1 decimal
          })
        }
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err)
        
        // Provide specific error messages based on error type
        let errorMessage = 'Failed to load dashboard data. Please try again.'
        
        if (err instanceof TypeError && err.message.includes('fetch')) {
          errorMessage = 'Cannot connect to the backend server. Please ensure the backend service is running on port 8100.'
        } else if (err instanceof Error && err.message.includes('404')) {
          errorMessage = 'API endpoint not found. Please check the backend configuration.'
        } else if (err instanceof Error && err.message.includes('500')) {
          errorMessage = 'Server error occurred. Please try again later.'
        } else if (err instanceof Error) {
          errorMessage = `Dashboard loading failed: ${err.message}`
        }
        
        setError(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [])

  const getStatusColor = (status: PlanStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'generating':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
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
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const handleDownload = async (planId: string, planName: string) => {
    if (downloadingPlan === planId) return
    
    try {
      setDownloadingPlan(planId)
      const blob = await apiClient.downloadPlan(planId, 'dxf')
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${planName.replace(/[^a-zA-Z0-9]/g, '_')}.dxf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
      setError('Failed to download plan. Please try again.')
    } finally {
      setDownloadingPlan(null)
    }
  }

  return (
    <div className="p-6 space-y-6 dark:bg-gray-900">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Welcome back! Here's an overview of your projects.</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link href="/plans/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Create New Plan</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Plans</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : stats.totalPlans}</div>
            <p className="text-xs text-muted-foreground">
              All time projects
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : stats.completedPlans}</div>
            <p className="text-xs text-muted-foreground">
              Successfully generated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : stats.generatingPlans}</div>
            <p className="text-xs text-muted-foreground">
              Currently generating
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Area</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : stats.totalArea}m²</div>
            <p className="text-xs text-muted-foreground">
              Across all projects
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Plans */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Plans</CardTitle>
                  <CardDescription>Your latest floor plan projects</CardDescription>
                </div>
                <Link href="/plans">
                  <Button variant="outline" size="sm">
                    View All
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {error ? (
                <div className="text-center py-8">
                  <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                  <Button onClick={() => window.location.reload()}>Retry</Button>
                </div>
              ) : isLoading ? (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <div key={i} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div className="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-lg animate-pulse"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4 mb-2 animate-pulse"></div>
                        <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2 animate-pulse"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : plans.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">No plans yet</p>
                  <Link href="/plans/new">
                    <Button>Create your first plan</Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {plans.map((plan) => (
                    <Link 
                      key={plan.id} 
                      href={`/plans/${plan.id}`}
                      className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors block"
                    >
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-6 h-6 text-blue-600" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{plan.name}</p>
                          <Badge className={getStatusColor(plan.status)}>
                            {getStatusText(plan.status)}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {plan.summary?.total_rooms || 0} rooms • {plan.dimensions.width}m × {plan.dimensions.height}m
                        </p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-xs text-gray-500">
                            {formatDate(plan.created_at)}
                          </span>
                          {(plan.progress || 0) < 100 && (
                            <div className="flex items-center space-x-2">
                              <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-1.5">
                                <div 
                                  className="bg-blue-600 h-1.5 rounded-full" 
                                  style={{ width: `${plan.progress || 0}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500 dark:text-gray-400">{plan.progress || 0}%</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center space-x-2" onClick={(e) => e.preventDefault()}>
                        {plan.status === 'completed' && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              handleDownload(plan.id, plan.name)
                            }}
                            disabled={downloadingPlan === plan.id}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            // TODO: Implement more options menu
                            console.log('More options for plan:', plan.id)
                          }}
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link href="/plans/new">
                <Button className="w-full justify-start" variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Create New Plan
                </Button>
              </Link>
              <Button className="w-full justify-start" variant="outline">
                <FileText className="w-4 h-4 mr-2" />
                Upload DXF File
              </Button>
              <Link href="/plans">
                <Button className="w-full justify-start" variant="outline">
                  <Clock className="w-4 h-4 mr-2" />
                  View Recent
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Backend service status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300">API Server</span>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">Online</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300">AI Engine</span>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">Ready</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300">Storage</span>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">Available</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}