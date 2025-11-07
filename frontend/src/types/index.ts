// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Plan Types
export interface Plan {
  id: string
  name: string
  status: PlanStatus
  created_at: string
  updated_at: string
  dimensions: {
    width: number
    height: number
  }
  rooms: Room[]
  constraints?: Record<string, any>
  building_type: string
  file_path?: string
  preview_data?: PreviewData
  summary?: PlanSummary
  progress?: number
  error?: string
}

export type PlanStatus = 
  | 'initializing'
  | 'generating'
  | 'optimizing'
  | 'validating'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface Room {
  id: string
  name: string
  type: RoomType
  area: number
  position?: {
    x: number
    y: number
  }
  dimensions?: {
    width: number
    height: number
  }
  polygon?: [number, number][]
  requirements?: string[]
  adjacency?: string[]
}

export type RoomType = 
  | 'bedroom'
  | 'living'
  | 'kitchen'
  | 'bathroom'
  | 'dining'
  | 'office'
  | 'garage'
  | 'storage'
  | 'balcony'
  | 'hallway'
  | 'stairs'
  | 'utility'
  | 'other'

export interface PreviewData {
  rooms_placed: number
  total_area: number
  file_size: number
  thumbnail?: string
  layers?: Layer[]
}

export interface Layer {
  id: string
  name: string
  visible: boolean
  color: string
  entities: any[]
}

export interface PlanSummary {
  total_rooms: number
  building_area: number
  file_size: number
  efficiency_score?: number
  compliance_score?: number
  ai_enhanced?: boolean
}

// Form Types
export interface FloorPlanRequest {
  name: string
  dimensions: {
    width: number
    height: number
  }
  rooms: RoomRequirement[]
  constraints?: Record<string, any>
  building_type: string
}

export interface RoomRequirement {
  type: RoomType
  area?: number
  preferred_width?: number
  preferred_depth?: number
  adjacency?: string[]
  requirements?: string[]
}

// Tool Types
export interface Tool {
  name: string
  description: string
  category: string
  parameters: ToolParameter[]
}

export interface ToolParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  required: boolean
  description?: string
  default?: any
  options?: any[]
}

export interface ToolRequest {
  tool_name: string
  parameters: Record<string, any>
}

export interface ToolResult {
  success: boolean
  data?: any
  error?: string
  execution_time: number
}

// UI State Types
export interface UIState {
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  loading: boolean
  notifications: Notification[]
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
}

// Canvas Types
export interface CanvasState {
  zoom: number
  pan: { x: number; y: number }
  selectedLayer?: string
  selectedTool?: string
  gridEnabled: boolean
  snapEnabled: boolean
  units: 'meters' | 'feet' | 'inches'
}

export interface Viewport {
  width: number
  height: number
  center: { x: number; y: number }
  scale: number
}

// CAD Types
export interface DXFEntity {
  type: string
  layer: string
  color: number
  properties: Record<string, any>
}

export interface CADDrawing {
  entities: DXFEntity[]
  layers: Layer[]
  units: string
  version: string
}

// WebSocket Types
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface PlanGenerationUpdate {
  plan_id: string
  status: PlanStatus
  progress: number
  message?: string
  error?: string
}

// Settings Types
export interface AppSettings {
  general: {
    theme: 'light' | 'dark' | 'system'
    language: string
    units: 'meters' | 'feet' | 'inches'
  }
  cad: {
    defaultLineWidth: number
    defaultFontSize: number
    gridSpacing: number
    snapTolerance: number
  }
  ai: {
    model: string
    temperature: number
    maxTokens: number
    autoOptimize: boolean
  }
  export: {
    defaultFormat: 'dxf' | 'pdf' | 'png'
    quality: 'low' | 'medium' | 'high'
    includeDimensions: boolean
    includeLayers: boolean
  }
}

// Chart Types
export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
}

// Statistics Types
export interface ProjectStats {
  totalPlans: number
  completedPlans: number
  failedPlans: number
  averageGenerationTime: number
  totalAreaGenerated: number
  popularRoomTypes: Array<{
    type: RoomType
    count: number
  }>
  generationTrend: Array<{
    date: string
    count: number
  }>
}

// Error Types
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: string
}

// Validation Types
export interface ValidationError {
  field: string
  message: string
  value?: any
}

// Export Types
export interface ExportOptions {
  format: 'dxf' | 'pdf' | 'png' | 'svg'
  quality?: 'low' | 'medium' | 'high'
  includeDimensions?: boolean
  includeLayers?: boolean
  scale?: number
  paperSize?: 'A4' | 'A3' | 'A2' | 'A1' | 'A0' | 'Custom'
}

// Search and Filter Types
export interface SearchFilters {
  query?: string
  status?: PlanStatus[]
  buildingType?: string[]
  dateRange?: {
    start: string
    end: string
  }
  areaRange?: {
    min: number
    max: number
  }
  roomsRange?: {
    min: number
    max: number
  }
}

export interface SortOptions {
  field: string
  direction: 'asc' | 'desc'
}