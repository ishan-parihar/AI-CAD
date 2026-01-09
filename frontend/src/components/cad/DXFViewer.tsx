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
import { Canvas, Line, Circle, Path, Text, Polyline, Rect } from 'fabric'

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
  // Additional properties that might exist on parsed entities
  x?: number
  y?: number
  x1?: number
  y1?: number
  x2?: number
  y2?: number
  insertPoint?: number[]
  vertices?: any[]
  points?: number[]
  startAngle?: number
  endAngle?: number
  rawEntity?: any
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
    console.log('🔍 DXF Viewer Debug: Creating DXF parser...')
    console.log('   Content length:', content.length)
    console.log('   Content preview:', content.substring(0, 200))
    
    try {
      // Create parser instance using statically imported DxfParser
      const parser = new DxfParser()
      
      console.log('🔍 DXF Viewer Debug: Parser created successfully')
      const dxf = parser.parseSync(content)
      console.log('🔍 DXF Viewer Debug: DXF parsed successfully')
      console.log('   Parsed object:', dxf)
      
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
      console.log('🔍 DXF Viewer Debug: Processing entities...')
      console.log('   Total entities:', dxf.entities.length)
      
      dxf.entities.forEach((entity: any, index: number) => {
        console.log(`🔍 DXF Viewer Debug: Entity ${index + 1}:`, {
          type: entity.type,
          layer: entity.layer,
          hasCoordinates: !!entity.coordinates,
          coordinatesLength: entity.coordinates?.length,
          startPoint: entity.startPoint,
          endPoint: entity.endPoint,
          radius: entity.radius,
          center: entity.center
        })
        
        // Debug: Show raw entity data to understand structure
        console.log(`🔍 Raw Entity ${index + 1} Data:`, entity)
        
        // Extract coordinates based on entity type and parser structure
        let coordinates: number[] | undefined
        let startPoint: number[] | undefined
        let endPoint: number[] | undefined
        
        if (entity.type === 'LWPOLYLINE') {
          // LWPOLYLINE coordinates are often in vertices or points
          if (entity.vertices && Array.isArray(entity.vertices)) {
            coordinates = entity.vertices.flatMap((v: any) => [v.x, v.y])
          } else if (entity.points && Array.isArray(entity.points)) {
            coordinates = entity.points.flat()
          } else if (entity.coordinates && Array.isArray(entity.coordinates)) {
            coordinates = entity.coordinates
          }
          console.log(`🔍 LWPOLYLINE coordinates extracted:`, coordinates)
        } else if (entity.type === 'LINE') {
          // LINE entities can store coordinates in different ways
          console.log(`🔍 Processing LINE entity - checking all possible coordinate locations:`)
          console.log(`   entity.vertices:`, entity.vertices)
          console.log(`   entity.coordinates:`, entity.coordinates)
          console.log(`   entity.startPoint:`, entity.startPoint)
          console.log(`   entity.endPoint:`, entity.endPoint)
          console.log(`   entity.x:`, entity.x, `entity.y:`, entity.y)
          console.log(`   entity.x1:`, entity.x1, `entity.y1:`, entity.y1)
          console.log(`   entity.x2:`, entity.x2, `entity.y2:`, entity.y2)
          
          // Try different coordinate storage patterns
          if (entity.vertices && Array.isArray(entity.vertices) && entity.vertices.length >= 2) {
            startPoint = [entity.vertices[0].x, entity.vertices[0].y]
            endPoint = [entity.vertices[1].x, entity.vertices[1].y]
            coordinates = [startPoint[0], startPoint[1], endPoint[0], endPoint[1]]
          } else if (entity.startPoint && entity.endPoint) {
            startPoint = entity.startPoint
            endPoint = entity.endPoint
            if (startPoint && endPoint) {
              coordinates = [startPoint[0], startPoint[1], endPoint[0], endPoint[1]]
            }
          } else if (entity.coordinates && Array.isArray(entity.coordinates) && entity.coordinates.length >= 4) {
            // Flat array [x1, y1, x2, y2]
            startPoint = [entity.coordinates[0], entity.coordinates[1]]
            endPoint = [entity.coordinates[2], entity.coordinates[3]]
            coordinates = entity.coordinates
          } else if (entity.x !== undefined && entity.y !== undefined && entity.x1 !== undefined && entity.y1 !== undefined) {
            // Individual coordinate properties
            startPoint = [entity.x, entity.y]
            endPoint = [entity.x1, entity.y1]
            coordinates = [startPoint[0], startPoint[1], endPoint[0], endPoint[1]]
          } else if (entity.x1 !== undefined && entity.y1 !== undefined && entity.x2 !== undefined && entity.y2 !== undefined) {
            // Individual coordinate properties (alternative naming)
            startPoint = [entity.x1, entity.y1]
            endPoint = [entity.x2, entity.y2]
            coordinates = [startPoint[0], startPoint[1], endPoint[0], endPoint[1]]
          }
          
          console.log(`🔍 LINE points extracted - start:`, startPoint, 'end:', endPoint, 'coordinates:', coordinates)
        } else if (entity.type === 'ARC') {
          // ARC entities have center, radius, and angles
          startPoint = entity.startPoint
          endPoint = entity.endPoint
          console.log(`🔍 ARC data extracted - center:`, entity.center, 'radius:', entity.radius)
        } else {
          // For other entity types, use the original properties
          coordinates = entity.coordinates
          startPoint = entity.startPoint
          endPoint = entity.endPoint
        }
        
        const dxfEntity: DXFEntity = {
          type: entity.type,
          layer: entity.layer || '0',
          color: entity.color || 7,
          handle: entity.handle || '',
          coordinates,
          startPoint,
          endPoint,
          radius: entity.radius,
          center: entity.center,
          angle: entity.angle,
          text: entity.text,
          // Store raw vertices for rendering fallback
          vertices: (entity as any).vertices,
          // Store the raw entity for deep debugging
          rawEntity: entity
        }

        console.log(`🔍 Created DXF entity:`, {
          type: dxfEntity.type,
          startPoint: dxfEntity.startPoint,
          endPoint: dxfEntity.endPoint,
          coordinates: dxfEntity.coordinates,
          vertices: dxfEntity.vertices
        })

        entities.push(dxfEntity)

        // Update bounds using extracted coordinates
        if (startPoint) {
          bounds.minX = Math.min(bounds.minX, startPoint[0])
          bounds.minY = Math.min(bounds.minY, startPoint[1])
          bounds.maxX = Math.max(bounds.maxX, startPoint[0])
          bounds.maxY = Math.max(bounds.maxY, startPoint[1])
        }
        if (endPoint) {
          bounds.minX = Math.min(bounds.minX, endPoint[0])
          bounds.minY = Math.min(bounds.minY, endPoint[1])
          bounds.maxX = Math.max(bounds.maxX, endPoint[0])
          bounds.maxY = Math.max(bounds.maxY, endPoint[1])
        }
        if (entity.center) {
          bounds.minX = Math.min(bounds.minX, entity.center[0] - (entity.radius || 0))
          bounds.minY = Math.min(bounds.minY, entity.center[1] - (entity.radius || 0))
          bounds.maxX = Math.max(bounds.maxX, entity.center[0] + (entity.radius || 0))
          bounds.maxY = Math.max(bounds.maxY, entity.center[1] + (entity.radius || 0))
        }
        
        // Update bounds from LWPOLYLINE coordinates
        if (coordinates && coordinates.length >= 2) {
          for (let i = 0; i < coordinates.length; i += 2) {
            bounds.minX = Math.min(bounds.minX, coordinates[i])
            bounds.minY = Math.min(bounds.minY, coordinates[i + 1])
            bounds.maxX = Math.max(bounds.maxX, coordinates[i])
            bounds.maxY = Math.max(bounds.maxY, coordinates[i + 1])
          }
        }

        // Add to layer
        const layer = layers.get(entity.layer || '0')
        if (layer) {
          layer.entities.push(dxfEntity)
        }
      })
    }

    // Initialize layer visibility (but don't set state here - handle it outside)
    const initialVisibility: Record<string, boolean> = {}
    layers.forEach((layer, name) => {
      initialVisibility[name] = true
    })

    const result = {
      layers,
      entities,
      bounds,
      units: (dxf as any).units || 'Units'
    }
    
    console.log('🔍 DXF Viewer Debug: Parsing complete:', {
      totalLayers: layers.size,
      totalEntities: entities.length,
      bounds,
      entityTypes: entities.reduce((acc, e) => {
        acc[e.type] = (acc[e.type] || 0) + 1
        return acc
      }, {} as Record<string, number>)
    })
    
    return result
    } catch (error) {
      console.error('🔍 DXF Viewer Debug: Error parsing DXF:', error)
      throw new Error(`DXF parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [])

  // Fit canvas to content (moved here before it's used)
  const fitToContent = useCallback((canvas: any, data: DXFData) => {
    console.log('📐 DXF Viewer Debug: === FITTING CONTENT TO CANVAS ===')
    
    if (!data.entities.length) {
      console.log('❌ No entities to fit')
      return
    }

    console.log('   Data bounds:', data.bounds)
    
    const padding = 50
    const canvasWidth = canvas.getWidth()
    const canvasHeight = canvas.getHeight()
    
    const contentWidth = (data.bounds.maxX - data.bounds.minX) * 10
    const contentHeight = (data.bounds.maxY - data.bounds.minY) * 10
    
    console.log('   Content dimensions:', { contentWidth, contentHeight })
    console.log('   Canvas dimensions:', { canvasWidth, canvasHeight })
    console.log('   Content bounds check:', {
      minX: data.bounds.minX,
      maxX: data.bounds.maxX,
      minY: data.bounds.minY,
      maxY: data.bounds.maxY,
      boundsValid: data.bounds.maxX > data.bounds.minX && data.bounds.maxY > data.bounds.minY
    })
    
    const scaleX = (canvasWidth - padding * 2) / contentWidth
    const scaleY = (canvasHeight - padding * 2) / contentHeight
    const scale = Math.min(scaleX, scaleY, 2) // Max zoom 2x
    
    console.log('🔍 DXF Viewer Debug: Calculated scale:', scale)
    
    setZoom(scale)
    canvas.setZoom(scale)
    
    // Center content
    const centerX = (canvasWidth - contentWidth * scale) / 2
    const centerY = (canvasHeight - contentHeight * scale) / 2
    canvas.absolutePan({ x: centerX, y: centerY })
    
    canvas.renderAll()
    console.log('🔍 DXF Viewer Debug: Content fitting complete')
  }, [])

  // Load DXF file
  const loadDXF = useCallback(async () => {
    if (!planId) return

    setIsLoading(true)
    setError(null)

    try {
      // Download DXF file from backend using API client
      const dxfBlob = await apiClient.downloadPlan(planId, 'dxf')
      
      if (!dxfBlob || dxfBlob.size === 0) {
        throw new Error('DXF file is empty or invalid')
      }

      // Convert blob to text for parsing
      const dxfContent = await dxfBlob.text()
      
      if (!dxfContent || dxfContent.trim() === '') {
        throw new Error('DXF file content is empty or invalid')
      }

      // Parse DXF content
      const parsedData = parseDXF(dxfContent)
      
      // Initialize layer visibility from parsed data
      const initialVisibility: Record<string, boolean> = {}
      parsedData.layers.forEach((layer, name) => {
        initialVisibility[name] = true
      })
      setLayerVisibility(initialVisibility)
      
      setDxfData(parsedData)
      onLoad?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load DXF file'
      setError(errorMessage)
      onError?.(err instanceof Error ? err : new Error(errorMessage))
    } finally {
      setIsLoading(false)
    }
  }, [planId, onLoad, onError])

  // Render DXF entities on canvas (moved here before it's used)
  const renderDXFEntities = useCallback((canvas: any, data: DXFData) => {
    console.log('🎨 DXF Viewer Debug: === STARTING RENDERING PHASE ===')
    console.log('   Canvas object:', canvas)
    console.log('   Canvas dimensions:', canvas ? { width: canvas.getWidth(), height: canvas.getHeight() } : 'null canvas')
    console.log('   Total entities to render:', data.entities.length)
    console.log('   Layer visibility:', layerVisibility)
    console.log('   Entity data preview:', data.entities.slice(0, 2).map(e => ({
      type: e.type,
      layer: e.layer,
      hasCoordinates: !!e.coordinates,
      hasVertices: !!(e as any).vertices,
      startPoint: e.startPoint,
      endPoint: e.endPoint
    })))
    
    const scale = 10 // Scale factor for better visibility
    const offsetX = 50
    const offsetY = 50
    
    let renderedCount = 0

    data.entities.forEach((entity, index) => {
      console.log(`🔍 DXF Viewer Debug: Rendering entity ${index + 1}:`, {
        type: entity.type,
        layer: entity.layer,
        visible: layerVisibility[entity.layer],
        coordinates: entity.coordinates,
        startPoint: entity.startPoint,
        endPoint: entity.endPoint
      })
      
      if (!layerVisibility[entity.layer]) {
        console.log(`   Skipping entity ${index + 1} - layer ${entity.layer} not visible`)
        return
      }

      let fabricObject: any = null
      const color = getColorFromIndex(entity.color)

      switch (entity.type) {
        case 'LINE':
          console.log(`🔍 Rendering LINE entity:`, {
            startPoint: entity.startPoint,
            endPoint: entity.endPoint,
            coordinates: entity.coordinates,
            vertices: (entity as any).vertices
          })
          
          // Try different coordinate sources for LINE entities
          let lineStart = entity.startPoint
          let lineEnd = entity.endPoint
          
          // If startPoint/endPoint are missing, try to extract from vertices or original entity
          if ((!lineStart || !lineEnd) && (entity as any).vertices && Array.isArray((entity as any).vertices) && (entity as any).vertices.length >= 2) {
            const vertices = (entity as any).vertices
            lineStart = [vertices[0].x, vertices[0].y]
            lineEnd = [vertices[1].x, vertices[1].y]
            console.log(`✅ Extracted LINE coordinates from stored vertices:`, { lineStart, lineEnd })
          } else if ((!lineStart || !lineEnd) && (entity as any).coordinates && Array.isArray((entity as any).coordinates) && (entity as any).coordinates.length >= 4) {
            const coords = (entity as any).coordinates
            lineStart = [coords[0], coords[1]]
            lineEnd = [coords[2], coords[3]]
            console.log(`✅ Extracted LINE coordinates from stored coordinates:`, { lineStart, lineEnd })
          } else {
            // Last resort: try to parse from raw entity data if available
            const rawEntity = (entity as any).rawEntity || (entity as any)._raw
            if (rawEntity && rawEntity.vertices && Array.isArray(rawEntity.vertices) && rawEntity.vertices.length >= 2) {
              const vertices = rawEntity.vertices
              lineStart = [vertices[0].x, vertices[0].y]
              lineEnd = [vertices[1].x, vertices[1].y]
              console.log(`✅ Extracted LINE coordinates from raw entity:`, { lineStart, lineEnd })
            }
          }
          
          if (lineStart && lineEnd && lineStart.length >= 2 && lineEnd.length >= 2) {
            fabricObject = new Line([
              lineStart[0] * scale + offsetX,
              lineStart[1] * scale + offsetY,
              lineEnd[0] * scale + offsetX,
              lineEnd[1] * scale + offsetY
            ], {
              stroke: color,
              strokeWidth: 1,
              selectable: false
            })
            console.log(`✅ Created LINE Fabric object`)
          } else {
            console.log(`❌ Failed to render LINE - missing coordinates:`, { lineStart, lineEnd })
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
          console.log(`🔍 Processing TEXT entity:`, {
            text: entity.text,
            startPoint: entity.startPoint,
            center: entity.center,
            x: entity.x, y: entity.y,
            insertPoint: entity.insertPoint,
            textData: entity
          })
          
          // TEXT entities can store position in different ways
          let textPosition: number[] | undefined = entity.startPoint
          if (!textPosition && entity.center) {
            textPosition = entity.center
          } else if (!textPosition && entity.x !== undefined && entity.y !== undefined) {
            textPosition = [entity.x, entity.y]
          } else if (!textPosition && entity.insertPoint) {
            textPosition = entity.insertPoint
          }
          
          console.log(`🔍 TEXT position extracted:`, textPosition)
          
          if (entity.text && textPosition && textPosition.length >= 2) {
            fabricObject = new Text(entity.text, {
              left: textPosition[0] * scale + offsetX,
              top: textPosition[1] * scale + offsetY,
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
        console.log(`   ✓ Created Fabric.js object for entity ${index + 1}:`, fabricObject)
        canvas.add(fabricObject)
        renderedCount++
      } else {
        console.log(`   ❌ Failed to create Fabric.js object for entity ${index + 1}`)
      }
    })

    console.log(`🎨 DXF Viewer Debug: === RENDERING COMPLETE ===`)
    console.log(`   Successfully rendered ${renderedCount} out of ${data.entities.length} entities`)
    console.log(`   Canvas objects count:`, canvas ? canvas.getObjects().length : 'null canvas')
    console.log(`   Canvas background:`, canvas ? canvas.backgroundColor : 'null canvas')
    
    if (canvas && canvas.getObjects().length > 0) {
      console.log(`   Canvas object types:`, canvas.getObjects().map((obj: any) => obj.type))
    } else {
      console.log(`   ⚠️  No objects on canvas - this is why the screen is blank!`)
    }
    
    canvas.renderAll()
    console.log(`   Canvas renderAll() called`)
  }, [layerVisibility])

  // Initialize Fabric.js canvas
  const initializeCanvas = useCallback(() => {
    console.log('🖼️ DXF Viewer Debug: === CANVAS INITIALIZATION ===')
    console.log('   Canvas element:', canvasRef.current)
    console.log('   Container element:', containerRef.current)
    console.log('   Container dimensions:', containerRef.current ? {
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight
    } : 'null container')
    console.log('   DXF data available:', !!dxfData)
    console.log('   DXF entities count:', dxfData ? dxfData.entities.length : 0)
    
    if (!canvasRef.current || !dxfData) {
      console.log('❌ Cannot initialize canvas - missing elements')
      return
    }

    // Dispose existing canvas
    if (fabricCanvasRef.current) {
      console.log('🔍 DXF Viewer Debug: Disposing existing canvas')
      fabricCanvasRef.current.dispose()
    }

    // Create new canvas using Canvas constructor
    const containerWidth = containerRef.current?.clientWidth || 800
    console.log('🔍 DXF Viewer Debug: Creating new canvas with width:', containerWidth)
    
    const canvas = new Canvas(canvasRef.current, {
      width: containerWidth,
      height: 600,
      backgroundColor: '#f8f9fa',
      selection: false
    })

    console.log('🖼️ DXF Viewer Debug: Canvas created successfully:', canvas)
    console.log('   Canvas initial dimensions:', { width: canvas.getWidth(), height: canvas.getHeight() })
    console.log('   Canvas background:', canvas.backgroundColor)
    fabricCanvasRef.current = canvas

    // Add a test rectangle to verify canvas is working
    try {
      const testRect = new Rect({
        left: 50,
        top: 50,
        width: 100,
        height: 100,
        fill: 'red',
        stroke: 'black',
        strokeWidth: 2
      })
      canvas.add(testRect)
      console.log('✅ Test rectangle added to canvas')
    } catch (error) {
      console.log('❌ Failed to add test rectangle:', error)
    }

    // Render DXF entities
    console.log('🖼️ DXF Viewer Debug: Starting entity rendering...')
    renderDXFEntities(canvas, dxfData)

    // Set initial zoom to fit content
    console.log('🖼️ DXF Viewer Debug: Fitting content to canvas...')
    fitToContent(canvas, dxfData)
    
    console.log('🖼️ DXF Viewer Debug: Canvas initialization complete')
    console.log('   Final canvas objects count:', canvas.getObjects().length)
    console.log('   Final canvas dimensions:', { width: canvas.getWidth(), height: canvas.getHeight() })
    console.log('   Final canvas zoom:', canvas.getZoom())
  }, [dxfData, renderDXFEntities, fitToContent])

  

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
  }, [planId])

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

  // Handle window resize and canvas sizing
  useEffect(() => {
    const handleResize = () => {
      console.log('🪟 DXF Viewer Debug: Window resize event')
      if (fabricCanvasRef.current && containerRef.current) {
        const newWidth = containerRef.current.clientWidth
        console.log('   Resizing canvas to:', { width: newWidth, height: 600 })
        fabricCanvasRef.current.setDimensions({
          width: newWidth,
          height: 600
        })
        fabricCanvasRef.current.renderAll()
      }
    }

    // Also log initial canvas setup
    setTimeout(() => {
      console.log('🪟 DXF Viewer Debug: Initial canvas setup check')
      console.log('   Container element:', containerRef.current)
      console.log('   Canvas element:', canvasRef.current)
      console.log('   Fabric canvas:', fabricCanvasRef.current)
      console.log('   Container computed style:', containerRef.current ? window.getComputedStyle(containerRef.current) : 'no container')
      
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect()
        console.log('   Canvas element rect:', rect)
        console.log('   Canvas element visible:', rect.width > 0 && rect.height > 0)
      }
    }, 1000)

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
    <div className={`space-y-4 ${className}`} style={{ minHeight: '700px', border: '2px solid blue', margin: '10px' }}>
      {/* Debug info */}
      <div className="bg-yellow-100 p-2 text-xs">
        Debug: Canvas Element={canvasRef.current ? 'EXISTS' : 'NULL'}, 
        Fabric Canvas={fabricCanvasRef.current ? 'EXISTS' : 'NULL'}, 
        DXF Data={dxfData ? `${dxfData.entities.length} entities` : 'NULL'}
      </div>
      
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
            className="border-4 border-green-500 rounded-lg overflow-hidden bg-white"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ 
              cursor: isDragging ? 'grabbing' : 'grab',
              minHeight: '600px',
              minWidth: '800px',
              position: 'relative'
            }}
          >
            <canvas 
              ref={canvasRef} 
              style={{
                border: '2px solid red',
                display: 'block'
              }}
            />
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