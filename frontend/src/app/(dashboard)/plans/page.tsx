'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  FileText, 
  Download, 
  Eye, 
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Grid3X3,
  List,
  Calendar,
  Building,
  MoreHorizontal
} from 'lucide-react'
import { Plan, PlanStatus } from '@/types'
import { apiClient } from '@/lib/api'

// Mock data for development
const mockPlans: Plan[] = [
  {
    id: '1',
    name: 'Modern Residential House',
    status: 'completed',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T11:45:00Z',
    dimensions: { width: 12.5, height: 8.0 },
    rooms: [
      { id: '1', name: 'Living Room', type: 'living', area: 25.5 },
      { id: '2', name: 'Master Bedroom', type: 'bedroom', area: 15.2 },
      { id: '3', name: 'Kitchen', type: 'kitchen', area: 12.0 }
    ],
    building_type: 'residential',
    progress: 100,
    summary: {
      total_rooms: 3,
      building_area: 100.0,
      file_size: 245760,
      efficiency_score: 92
    }
  },
  {
    id: '2',
    name: 'Office Floor Layout',
    status: 'generating',
    created_at: '2024-01-15T14:20:00Z',
    updated_at: '2024-01-15T14:25:00Z',
    dimensions: { width: 20.0, height: 15.0 },
    rooms: [
      { id: '1', name: 'Open Office', type: 'office', area: 120.0 },
      { id: '2', name: 'Meeting Room', type: 'office', area: 20.0 }
    ],
    building_type: 'commercial',
    progress: 65,
    summary: {
      total_rooms: 2,
      building_area: 300.0,
      file_size: 0,
      efficiency_score: 0
    }
  },
  {
    id: '3',
    name: 'Compact Apartment',
    status: 'failed',
    created_at: '2024-01-14T09:15:00Z',
    updated_at: '2024-01-14T09:45:00Z',
    dimensions: { width: 8.0, height: 6.0 },
    rooms: [
      { id: '1', name: 'Studio Room', type: 'living', area: 30.0 },
      { id: '2', name: 'Small Kitchen', type: 'kitchen', area: 8.0 }
    ],
    building_type: 'residential',
    progress: 25,
    summary: {
      total_rooms: 2,
      building_area: 48.0,
      file_size: 0,
      efficiency_score: 0
    }
  },
  {
    id: '4',
    name: 'Retail Store Design',
    status: 'completed',
    created_at: '2024-01-13T16:30:00Z',
    updated_at: '2024-01-13T17:20:00Z',
    dimensions: { width: 15.0, height: 10.0 },
    rooms: [
      { id: '1', name: 'Sales Floor', type: 'office', area: 100.0 },
      { id: '2', name: 'Storage', type: 'storage', area: 25.0 },
      { id: '3', name: 'Office', type: 'office', area: 15.0 }
    ],
    building_type: 'commercial',
    progress: 100,
    summary: {
      total_rooms: 3,
      building_area: 150.0,
      file_size: 312450,
      efficiency_score: 88
    }
  }
]

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<PlanStatus | 'all'>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })

  // Fetch real data from API
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Build filters
        const filters: any = {}
        if (searchTerm) filters.query = searchTerm
        if (statusFilter !== 'all') filters.status = [statusFilter]
        if (typeFilter !== 'all') filters.buildingType = [typeFilter]
        
        const response = await apiClient.listPlans(
          filters,
          { field: 'updated_at', direction: 'desc' },
          pagination.page,
          pagination.limit
        )
        
        if (response.success && response.data) {
          setPlans(response.data)
          if (response.pagination) {
            setPagination(response.pagination)
          }
        }
      } catch (err) {
        console.error('Failed to fetch plans:', err)
        setError('Failed to load plans. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchPlans()
  }, [searchTerm, statusFilter, typeFilter, pagination.page])

  const getStatusColor = (status: PlanStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'generating':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'failed':
        return 'bg-destructive/10 text-destructive dark:bg-destructive/20'
      case 'initializing':
        return 'bg-warning/10 text-warning dark:bg-warning/20'
      default:
        return 'bg-muted text-foreground dark:bg-muted/50'
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

  const filteredPlans = plans.filter(plan => {
    const matchesSearch = plan.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || plan.status === statusFilter
    const matchesType = typeFilter === 'all' || plan.building_type === typeFilter
    return matchesSearch && matchesStatus && matchesType
  })

  const handleDownload = async (planId: string) => {
    try {
      // const response = await apiClient.downloadPlan(planId)
      console.log('Downloading plan:', planId)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDelete = async (planId: string) => {
    if (confirm('Are you sure you want to delete this plan?')) {
      try {
        // await apiClient.deletePlan(planId)
        setPlans(plans.filter(plan => plan.id !== planId))
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  }

  const PlanCard = ({ plan }: { plan: Plan }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg truncate">{plan.name}</CardTitle>
            <CardDescription className="flex items-center space-x-2 mt-1">
              <Building className="w-4 h-4" />
              <span className="capitalize">{plan.building_type}</span>
              <span>•</span>
              <span>{plan.dimensions.width}m × {plan.dimensions.height}m</span>
            </CardDescription>
          </div>
          <Badge className={getStatusColor(plan.status)}>
            {getStatusText(plan.status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Plan Details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Rooms:</span>
              <span className="ml-2 font-medium">{plan.summary?.total_rooms || 0}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Area:</span>
              <span className="ml-2 font-medium">{plan.summary?.building_area || 0}m²</span>
            </div>
            {plan.summary?.file_size && plan.summary.file_size > 0 && (
              <div>
                <span className="text-muted-foreground">File:</span>
                <span className="ml-2 font-medium">{formatFileSize(plan.summary.file_size)}</span>
              </div>
            )}
            {plan.summary?.efficiency_score && plan.summary.efficiency_score > 0 && (
              <div>
                <span className="text-muted-foreground">Score:</span>
                <span className="ml-2 font-medium">{plan.summary.efficiency_score}%</span>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {(plan.progress || 0) < 100 && (
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{plan.progress || 0}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${plan.progress || 0}%` }}
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center space-x-2">
              <Link href={`/plans/${plan.id}`}>
                <Button variant="outline" size="sm">
                  <Eye className="w-4 h-4 mr-1" />
                  View
                </Button>
              </Link>
              {plan.status === 'completed' && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownload(plan.id)}
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </Button>
              )}
            </div>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const PlanListItem = ({ plan }: { plan: Plan }) => (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-medium truncate">{plan.name}</h3>
                <Badge className={getStatusColor(plan.status)}>
                  {getStatusText(plan.status)}
                </Badge>
              </div>
              <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                <span className="capitalize">{plan.building_type}</span>
                <span>•</span>
                <span>{plan.dimensions.width}m × {plan.dimensions.height}m</span>
                <span>•</span>
                <span>{plan.summary?.total_rooms || 0} rooms</span>
                <span>•</span>
                <span>{formatDate(plan.created_at)}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {plan.status === 'completed' && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handleDownload(plan.id)}
              >
                <Download className="w-4 h-4" />
              </Button>
            )}
            <Link href={`/plans/${plan.id}`}>
              <Button variant="outline" size="sm">
                <Eye className="w-4 h-4" />
              </Button>
            </Link>
            <Button variant="outline" size="sm">
              <Edit className="w-4 h-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => handleDelete(plan.id)}
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Plans</h1>
          <p className="text-muted-foreground">Manage and view your floor plan projects</p>
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

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search plans..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-4">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="generating">Generating</option>
                <option value="failed">Failed</option>
                <option value="initializing">Initializing</option>
              </select>

              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="all">All Types</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="mixed">Mixed Use</option>
              </select>

              {/* View Mode Toggle */}
              <div className="flex items-center border border-input rounded-md">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="rounded-r-none"
                >
                  <Grid3X3 className="w-4 h-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="rounded-l-none"
                >
                  <List className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          Showing {filteredPlans.length} of {plans.length} plans
        </p>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            More Filters
          </Button>
        </div>
      </div>

      {/* Plans Display */}
      {filteredPlans.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No plans found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first floor plan'
              }
            </p>
            <Link href="/plans/new">
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Create New Plan</span>
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPlans.map(plan => (
                <PlanCard key={plan.id} plan={plan} />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredPlans.map(plan => (
                <PlanListItem key={plan.id} plan={plan} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}