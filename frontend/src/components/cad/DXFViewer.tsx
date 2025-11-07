'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  ZoomIn, 
  ZoomOut, 
  Move, 
  Download, 
  Maximize2, 
  Layers,
  Ruler,
  Eye,
  EyeOff,
  RotateCcw,
  Loader,
  AlertCircle
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import DxfParser from 'dxf-parser'
import { Canvas, Line, Circle, Path, Text, Polyline } from 'fabric'

// Fabric.js types (dynamic import)
interface FabricCanvas {
  dispose(): void
  add(obj: any): void
  setZoom(zoom: number): void
  renderAll(): void
  absolutePan(point: { x: number; y: number }): void
  toDataURL(options?: any): string
  clear(): void
  setDimensions(dimensions: { width: number; height: number }): void
  getZoom(): number
  getWidth(): number
  getHeight(): number
}

type FabricModule = any

// DXF parsing types
interface DXFEntity {
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
}

interface DXFLayer {
  name: string
  color: number
  visible: boolean
  entities: DXFEntity[]
}

interface DXFData {
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

interface DXFViewerProps {
  planId: string
  onLoad?: () => void
  onError?: (error: Error) => void
  className?: string
}

export default function DXFViewer({ planId, onLoad, onError, className }: DXFViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const fabricCanvasRef = useRef<FabricCanvas | null>(null)
  
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dxfData, setDxfData] = useState<DXFData | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [showLayers, setShowLayers] = useState(true)
  const [showRulers, setShowRulers] = useState(true)
  const [selectedLayer, setSelectedLayer] = useState<string | null>(null)
  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({})

  // Parse DXF content
  const parseDXF = useCallback((content: string): DXFData => {
    console.log('Creating DXF parser...')
    
    try {
      // Create parser instance using statically imported DxfParser
      const parser = new DxfParser()
      
      console.log('Parser created successfully:', parser)
      const dxf = parser.parseSync(content)
      console.log('DXF parsed successfully')
      
      if (!dxf) {
        throw new Error('Failed to parse DXF content - result is null')
      }
      
      const layers = new Map<string, DXFLayer>()
      const entities: DXFEntity[] = []
      let bounds = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }

    // Process layers
    if (dxf.tables?.layer?.layers) {
      Object.entries(dxf.tables.layer.layers).forEach(([name, layer]: [string, any]) => {
        layers.set(name, {
          name,
          color: layer.color || 7,
          visible: true,
          entities: []
        })
      })
    }

    // Process entities
    if (dxf.entities) {
      dxf.entities.forEach((entity: any) => {
        const dxfEntity: DXFEntity = {
          type: entity.type,
          layer: entity.layer || '0',
          color: entity.color || 7,
          handle: entity.handle || '',
          coordinates: entity.coordinates,
          startPoint: entity.startPoint,
          endPoint: entity.endPoint,
          radius: entity.radius,
          center: entity.center,
          angle: entity.angle,
          text: entity.text
        }

        entities.push(dxfEntity)

        // Update bounds
        if (entity.startPoint) {
          bounds.minX = Math.min(bounds.minX, entity.startPoint[0])
          bounds.minY = Math.min(bounds.minY, entity.startPoint[1])
          bounds.maxX = Math.max(bounds.maxX, entity.startPoint[0])
          bounds.maxY = Math.max(bounds.maxY, entity.startPoint[1])
        }
        if (entity.endPoint) {
          bounds.minX = Math.min(bounds.minX, entity.endPoint[0])
          bounds.minY = Math.min(bounds.minY, entity.endPoint[1])
          bounds.maxX = Math.max(bounds.maxX, entity.endPoint[0])
          bounds.maxY = Math.max(bounds.maxY, entity.endPoint[1])
        }
        if (entity.center) {
          bounds.minX = Math.min(bounds.minX, entity.center[0] - (entity.radius || 0))
          bounds.minY = Math.min(bounds.minY, entity.center[1] - (entity.radius || 0))
          bounds.maxX = Math.max(bounds.maxX, entity.center[0] + (entity.radius || 0))
          bounds.maxY = Math.max(bounds.maxY, entity.center[1] + (entity.radius || 0))
        }

        // Add to layer
        const layer = layers.get(entity.layer || '0')
        if (layer) {
          layer.entities.push(dxfEntity)
        }
      })
    }

    // Initialize layer visibility
    const initialVisibility: Record<string, boolean> = {}
    layers.forEach((layer, name) => {
      initialVisibility[name] = true
    })

    setLayerVisibility(initialVisibility)

    return {
      layers,
      entities,
      bounds,
      units: (dxf as any).units || 'Units'
    }
    } catch (error) {
      console.error('Error parsing DXF:', error)
      throw new Error(`DXF parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [])

  // Load DXF file
  const loadDXF = useCallback(async () => {
    if (!planId) return

    setIsLoading(true)
    setError(null)

    try {
      // Download DXF file from backend
      const response = await fetch(`/api/v1/plans/${planId}/download`)
      if (!response.ok) {
        throw new Error(`Failed to download DXF: ${response.statusText}`)
      }

      const dxfContent = await response.text()
      
      if (!dxfContent || dxfContent.trim() === '') {
        throw new Error('DXF file is empty or invalid')
      }

      // Parse DXF content
      const parsedData = parseDXF(dxfContent)
      setDxfData(parsedData)
      onLoad?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load DXF file'
      setError(errorMessage)
      onError?.(err instanceof Error ? err : new Error(errorMessage))
    } finally {
      setIsLoading(false)
    }
  }, [planId, parseDXF, onLoad, onError])

  // Initialize Fabric.js canvas
  const initializeCanvas = useCallback(() => {
    if (!canvasRef.current || !dxfData) return

    // Dispose existing canvas
    if (fabricCanvasRef.current) {
      fabricCanvasRef.current.dispose()
    }

    // Create new canvas using Canvas constructor
    const canvas = new Canvas(canvasRef.current, {
      width: containerRef.current?.clientWidth || 800,
      height: 600,
      backgroundColor: '#f8f9fa',
      selection: false
    })

    fabricCanvasRef.current = canvas

    // Render DXF entities
    renderDXFEntities(canvas, dxfData)

    // Set initial zoom to fit content
    fitToContent(canvas, dxfData)
  }, [dxfData])

  // Render DXF entities on canvas
  const renderDXFEntities = useCallback((canvas: any, data: DXFData) => {
    const scale = 10 // Scale factor for better visibility
    const offsetX = 50
    const offsetY = 50

    data.entities.forEach(entity => {
      if (!layerVisibility[entity.layer]) return

      let fabricObject: any = null
      const color = getColorFromIndex(entity.color)

      switch (entity.type) {
        case 'LINE':
          if (entity.startPoint && entity.endPoint) {
            fabricObject = new Line([
              entity.startPoint[0] * scale + offsetX,
              entity.startPoint[1] * scale + offsetY,
              entity.endPoint[0] * scale + offsetX,
              entity.endPoint[1] * scale + offsetY
            ], {
              stroke: color,
              strokeWidth: 1,
              selectable: false
            })
          }
          break

        case 'CIRCLE':
          if (entity.center && entity.radius) {
            fabricObject = new Circle({
              left: (entity.center[0] - entity.radius) * scale + offsetX,
              top: (entity.center[1] - entity.radius) * scale + offsetY,
              radius: entity.radius * scale,
              fill: 'transparent',
              stroke: color,
              strokeWidth: 1,
              selectable: false
            })
          }
          break

        case 'ARC':
          // Convert arc to path
          if (entity.center && entity.radius && 
              (entity as any).startAngle !== undefined && 
              (entity as any).endAngle !== undefined) {
            const path = createArcPath(
              entity.center[0] * scale + offsetX,
              entity.center[1] * scale + offsetY,
              entity.radius * scale,
              (entity as any).startAngle,
              (entity as any).endAngle
            )
            fabricObject = new Path(path, {
              fill: 'transparent',
              stroke: color,
              strokeWidth: 1,
              selectable: false
            })
          }
          break

        case 'TEXT':
          if (entity.text && entity.startPoint) {
            fabricObject = new Text(entity.text, {
              left: entity.startPoint[0] * scale + offsetX,
              top: entity.startPoint[1] * scale + offsetY,
              fontSize: 12,
              fill: color,
              selectable: false
            })
          }
          break

        case 'POLYLINE':
        case 'LWPOLYLINE':
          if (entity.coordinates && entity.coordinates.length >= 2 && entity.coordinates.length % 2 === 0) {
            if (entity.type === 'LWPOLYLINE') {
              // Convert flat array to points array
              const pointPairs = []
              for (let i = 0; i < entity.coordinates.length; i += 2) {
                pointPairs.push({ 
                  x: entity.coordinates[i] * scale + offsetX, 
                  y: entity.coordinates[i + 1] * scale + offsetY 
                })
              }
              fabricObject = new Polyline(pointPairs, {
                fill: 'transparent',
                stroke: color,
                strokeWidth: 1,
                selectable: false
              })
            } else {
              const points = entity.coordinates.map((coord: number, index: number) => {
                if (index % 2 === 0) {
                  return { x: coord * scale + offsetX }
                }
                return { y: coord * scale + offsetY }
              }).reduce((acc: any[], point: any, index: number) => {
                if (index % 2 === 0) {
                  acc.push({ x: point.x, y: entity.coordinates![index + 1] * scale + offsetY })
                }
                return acc
              }, [])
              
              fabricObject = new Polyline(points, {
                fill: 'transparent',
                stroke: color,
                strokeWidth: 1,
                selectable: false
              })
            }
          }
          break
      }

      if (fabricObject) {
        canvas.add(fabricObject)
      }
    })

    canvas.renderAll()
  }, [layerVisibility])

  // Helper function to create arc path
  const createArcPath = (cx: number, cy: number, radius: number, startAngle: number, endAngle: number): string => {
    const start = polarToCartesian(cx, cy, radius, endAngle)
    const end = polarToCartesian(cx, cy, radius, startAngle)
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1"
    return [
      "M", start.x, start.y,
      "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(" ")
  }

  const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    }
  }

  // Helper function to get color from AutoCAD color index
  const getColorFromIndex = (colorIndex: number): string => {
    const colors: Record<number, string> = {
      1: '#ff0000', 2: '#ffff00', 3: '#00ff00', 4: '#00ffff',
      5: '#0000ff', 6: '#ff00ff', 7: '#ffffff', 8: '#808080',
      9: '#404040', 10: '#ff8080', 11: '#ffff80', 12: '#80ff80',
      13: '#80ffff', 14: '#8080ff', 15: '#ff80ff', 16: '#c0c0c0',
      17: '#804040', 18: '#808000', 19: '#408000', 20: '#408080',
      21: '#004080', 22: '#404080', 23: '#800080', 24: '#804040',
      25: '#ffffff'
    }
    return colors[colorIndex] || '#ffffff'
  }

  // Fit canvas to content
  const fitToContent = useCallback((canvas: any, data: DXFData) => {
    if (!data.entities.length) return

    const padding = 50
    const canvasWidth = canvas.getWidth()
    const canvasHeight = canvas.getHeight()
    
    const contentWidth = (data.bounds.maxX - data.bounds.minX) * 10
    const contentHeight = (data.bounds.maxY - data.bounds.minY) * 10
    
    const scaleX = (canvasWidth - padding * 2) / contentWidth
    const scaleY = (canvasHeight - padding * 2) / contentHeight
    const scale = Math.min(scaleX, scaleY, 2) // Max zoom 2x
    
    setZoom(scale)
    canvas.setZoom(scale)
    
    // Center content
    const centerX = (canvasWidth - contentWidth * scale) / 2
    const centerY = (canvasHeight - contentHeight * scale) / 2
    canvas.absolutePan({ x: centerX, y: centerY })
    
    canvas.renderAll()
  }, [])

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    if (!fabricCanvasRef.current) return
    const newZoom = Math.min(zoom * 1.2, 5)
    setZoom(newZoom)
    fabricCanvasRef.current.setZoom(newZoom)
    fabricCanvasRef.current.renderAll()
  }, [zoom])

  const handleZoomOut = useCallback(() => {
    if (!fabricCanvasRef.current) return
    const newZoom = Math.max(zoom / 1.2, 0.1)
    setZoom(newZoom)
    fabricCanvasRef.current.setZoom(newZoom)
    fabricCanvasRef.current.renderAll()
  }, [zoom])

  const handleZoomReset = useCallback(() => {
    if (!fabricCanvasRef.current || !dxfData) return
    fitToContent(fabricCanvasRef.current, dxfData)
  }, [dxfData, fitToContent])

  // Pan controls
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }, [pan])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging || !fabricCanvasRef.current) return
    
    const newX = e.clientX - dragStart.x
    const newY = e.clientY - dragStart.y
    
    setPan({ x: newX, y: newY })
    fabricCanvasRef.current.absolutePan({ x: newX, y: newY })
  }, [isDragging, dragStart])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  // Layer visibility toggle
  const toggleLayerVisibility = useCallback((layerName: string) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layerName]: !prev[layerName]
    }))
  }, [])

  // Export functions
  const handleExportPNG = useCallback(() => {
    if (!fabricCanvasRef.current) return
    
    const dataURL = fabricCanvasRef.current.toDataURL({
      format: 'png',
      quality: 1,
      multiplier: 2
    })
    
    const link = document.createElement('a')
    link.download = `floor-plan-${planId}.png`
    link.href = dataURL
    link.click()
  }, [planId])

  const handleFullscreen = useCallback(() => {
    if (!containerRef.current) return
    
    if (containerRef.current.requestFullscreen) {
      containerRef.current.requestFullscreen()
    }
  }, [])

  // Load DXF when planId changes
  useEffect(() => {
    if (planId) {
      loadDXF()
    }
  }, [planId, loadDXF])

  // Initialize canvas when DXF data is loaded
  useEffect(() => {
    if (dxfData) {
      initializeCanvas()
    }
  }, [dxfData, initializeCanvas])

  // Re-render when layer visibility changes
  useEffect(() => {
    if (fabricCanvasRef.current && dxfData) {
      fabricCanvasRef.current.clear()
      renderDXFEntities(fabricCanvasRef.current, dxfData)
    }
  }, [layerVisibility, dxfData, renderDXFEntities])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (fabricCanvasRef.current && containerRef.current) {
        fabricCanvasRef.current.setDimensions({
          width: containerRef.current.clientWidth,
          height: 600
        })
        fabricCanvasRef.current.renderAll()
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96 bg-muted rounded-lg">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading DXF file...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96 bg-muted rounded-lg">
        <div className="text-center max-w-md">
          <AlertCircle className="w-8 h-8 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">Failed to Load DXF</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={loadDXF} variant="outline">
            <RotateCcw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 bg-muted rounded-lg">
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleZoomIn}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleZoomOut}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleZoomReset}>
            <RotateCcw className="w-4 h-4" />
          </Button>
          <div className="px-3 py-1 bg-background rounded border text-sm">
            {Math.round(zoom * 100)}%
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => setShowRulers(!showRulers)}>
            <Ruler className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowLayers(!showLayers)}>
            <Layers className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportPNG}>
            <Download className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleFullscreen}>
            <Maximize2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex space-x-4">
        {/* Main Canvas */}
        <div className="flex-1">
          <div 
            ref={containerRef}
            className="border rounded-lg overflow-hidden bg-white"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
          >
            <canvas ref={canvasRef} />
          </div>
        </div>

        {/* Layers Panel */}
        {showLayers && dxfData && (
          <div className="w-64 bg-muted rounded-lg p-4">
            <h3 className="font-medium text-foreground mb-3 flex items-center">
              <Layers className="w-4 h-4 mr-2" />
              Layers
            </h3>
            <div className="space-y-2">
              {Array.from(dxfData.layers.entries()).map(([name, layer]) => (
                <div 
                  key={name}
                  className="flex items-center justify-between p-2 bg-background rounded border"
                >
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleLayerVisibility(name)}
                      className="p-1 hover:bg-muted rounded"
                    >
                      {layerVisibility[name] ? (
                        <Eye className="w-4 h-4 text-foreground" />
                      ) : (
                        <EyeOff className="w-4 h-4 text-muted-foreground" />
                      )}
                    </button>
                    <div 
                      className="w-3 h-3 rounded border"
                      style={{ backgroundColor: getColorFromIndex(layer.color) }}
                    />
                    <span className="text-sm text-foreground">{name}</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {layer.entities.length}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}