// CAD-related TypeScript types

export interface DXFEntity {
  type: string
  layer: string
  color: number
  handle: string
  coordinates?: number[]
  startPoint?: number[]
  endPoint?: number[]
  radius?: number
  center?: number[]
  angle?: number
  text?: string
  startAngle?: number
  endAngle?: number
}

export interface DXFLayer {
  name: string
  color: number
  visible: boolean
  entities: DXFEntity[]
}

export interface DXFData {
  layers: Map<string, DXFLayer>
  entities: DXFEntity[]
  bounds: {
    minX: number
    minY: number
    maxX: number
    maxY: number
  }
  units: string
}

export interface Point2D {
  x: number
  y: number
}

export interface Point3D {
  x: number
  y: number
  z: number
}

export interface BoundingBox {
  min: Point2D
  max: Point2D
  width: number
  height: number
}

export interface LayerVisibility {
  [layerName: string]: boolean
}

export interface ViewerState {
  zoom: number
  pan: Point2D
  isDragging: boolean
  selectedLayer: string | null
  showLayers: boolean
  showRulers: boolean
  layerVisibility: LayerVisibility
}

export interface DrawingInfo {
  totalEntities: number
  totalLayers: number
  bounds: BoundingBox
  units: string
  version: string
}

export interface MeasurementTool {
  id: string
  type: 'distance' | 'area' | 'angle'
  points: Point2D[]
  result?: number
  unit: string
}

export interface ExportOptions {
  format: 'png' | 'jpg' | 'svg' | 'pdf'
  quality?: number
  scale?: number
  backgroundColor?: string
  showDimensions?: boolean
}

export interface ViewerSettings {
  backgroundColor: string
  gridEnabled: boolean
  snapToGrid: boolean
  gridSize: number
  showCoordinates: boolean
  antialiasing: boolean
  highQuality: boolean
}

// Fabric.js related types for the canvas
export interface FabricObject {
  type: string
  left: number
  top: number
  fill?: string
  stroke?: string
  strokeWidth?: number
  selectable: boolean
  evented: boolean
}

export interface FabricLine extends FabricObject {
  x1: number
  y1: number
  x2: number
  y2: number
}

export interface FabricCircle extends FabricObject {
  radius: number
  originX: string
  originY: string
}

export interface FabricPath extends FabricObject {
  path: string
}

export interface FabricText extends FabricObject {
  text: string
  fontSize: number
  fontFamily: string
}

export interface FabricPolyline extends FabricObject {
  points: Point2D[]
}

// AutoCAD color index mapping
export const AUTOCAD_COLORS: Record<number, string> = {
  1: '#ff0000', 2: '#ffff00', 3: '#00ff00', 4: '#00ffff',
  5: '#0000ff', 6: '#ff00ff', 7: '#ffffff', 8: '#808080',
  9: '#404040', 10: '#ff8080', 11: '#ffff80', 12: '#80ff80',
  13: '#80ffff', 14: '#8080ff', 15: '#ff80ff', 16: '#c0c0c0',
  17: '#804040', 18: '#808000', 19: '#408000', 20: '#408080',
  21: '#004080', 22: '#404080', 23: '#800080', 24: '#804040',
  25: '#ffffff', 250: '#003f7f', 251: '#007faa', 252: '#00aaff',
  253: '#40ffff', 254: '#80ffff', 255: '#c0ffff'
}

// DXF entity types
export type DXFEntityType = 
  | 'LINE'
  | 'CIRCLE'
  | 'ARC'
  | 'TEXT'
  | 'MTEXT'
  | 'POLYLINE'
  | 'LWPOLYLINE'
  | 'POINT'
  | 'ELLIPSE'
  | 'SPLINE'
  | 'HATCH'
  | 'DIMENSION'
  | 'INSERT'
  | 'BLOCK'
  | '3DFACE'
  | 'SOLID'
  | 'TRACE'
  | 'RAY'
  | 'XLINE'
  | 'MLEADER'

// Viewer events
export interface ViewerEvent {
  type: 'click' | 'mousemove' | 'zoom' | 'pan' | 'select' | 'layer_toggle'
  position: Point2D
  target?: DXFEntity | DXFLayer
  data?: any
}

export interface ViewerCallbacks {
  onEntityClick?: (entity: DXFEntity, position: Point2D) => void
  onLayerToggle?: (layerName: string, visible: boolean) => void
  onZoom?: (zoom: number) => void
  onPan?: (pan: Point2D) => void
  onSelection?: (entities: DXFEntity[]) => void
  onMeasurement?: (measurement: MeasurementTool) => void
}