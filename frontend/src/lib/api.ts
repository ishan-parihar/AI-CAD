import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { 
  ApiResponse, 
  Plan, 
  FloorPlanRequest, 
  ToolRequest, 
  ToolResult, 
  PaginatedResponse,
  SearchFilters,
  SortOptions,
  ProjectStats
} from '@/types'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    const response = await this.client.get('/api/v1/health')
    return response.data
  }

  // Plans API
  async generatePlan(request: FloorPlanRequest): Promise<{ plan_id: string; status: string }> {
    const response = await this.client.post('/api/v1/plans/generate', request)
    return response.data
  }

  async getPlanStatus(planId: string): Promise<Plan> {
    const response = await this.client.get(`/api/v1/plans/${planId}/status`)
    return response.data
  }

  async getPlanPreview(planId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/plans/${planId}/preview`)
    return response.data
  }

  async downloadPlan(planId: string, format: string = 'dxf'): Promise<Blob> {
    const response = await this.client.get(
      `/api/v1/plans/${planId}/download?file_format=${format}`,
      { responseType: 'blob' }
    )
    return response.data
  }

  async listPlans(
    filters?: SearchFilters,
    sort?: SortOptions,
    page = 1,
    limit = 20
  ): Promise<PaginatedResponse<Plan>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    })

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v.toString()))
          } else {
            params.append(key, value.toString())
          }
        }
      })
    }

    if (sort) {
      params.append('sort', sort.field)
      params.append('order', sort.direction)
    }

    const response = await this.client.get(`/api/v1/plans?${params}`)
    
    // Backend returns {plans: [...]} but frontend expects {data: [...], pagination: {...}}
    const backendData = response.data
    return {
      success: true,
      data: backendData.plans || [],
      pagination: {
        page: page,
        limit: limit,
        total: backendData.plans?.length || 0,
        totalPages: Math.ceil((backendData.plans?.length || 0) / limit)
      }
    }
  }

  async deletePlan(planId: string): Promise<ApiResponse> {
    const response = await this.client.delete(`/api/v1/plans/${planId}`)
    return response.data
  }

  // Tools API
  async listTools(): Promise<{ tools: any[] }> {
    const response = await this.client.get('/api/v1/tools')
    return response.data
  }

  async executeTool(request: ToolRequest): Promise<ToolResult> {
    const response = await this.client.post('/api/v1/tools/execute', request)
    return response.data
  }

  // Statistics API
  async getProjectStats(): Promise<ProjectStats> {
    const response = await this.client.get('/api/v1/stats')
    return response.data
  }

  // File Upload API
  async uploadFile(file: File, type: string): Promise<{ url: string; id: string }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)

    const response = await this.client.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  // Settings API
  async getSettings(): Promise<any> {
    const response = await this.client.get('/api/v1/settings')
    return response.data
  }

  async updateSettings(settings: any): Promise<ApiResponse> {
    const response = await this.client.put('/api/v1/settings', settings)
    return response.data
  }

  // User API
  async getProfile(): Promise<any> {
    const response = await this.client.get('/api/v1/user/profile')
    return response.data
  }

  async updateProfile(profile: any): Promise<ApiResponse> {
    const response = await this.client.put('/api/v1/user/profile', profile)
    return response.data
  }

  // Authentication API (if implemented)
  async login(credentials: { email: string; password: string }): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/login', credentials)
    return response.data
  }

  async logout(): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/logout')
    return response.data
  }

  async register(userData: {
    email: string
    password: string
    name: string
  }): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/register', userData)
    return response.data
  }
}

// Create singleton instance
const apiClient = new ApiClient()

// Export types for external use
export type { ApiClient }
export { apiClient }