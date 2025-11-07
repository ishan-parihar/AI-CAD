'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/lib/api'
import { FloorPlanRequest } from '@/types'
import { 
  ArrowLeft, 
  ArrowRight, 
  Plus, 
  Minus, 
  Save,
  Home,
  Ruler,
  Settings,
  Check
} from 'lucide-react'

interface Room {
  id: string
  name: string
  type: string
  min_area: number
  max_area: number
  requirements: string[]
}

interface PlanData {
  name: string
  building_type: 'residential' | 'commercial' | 'mixed'
  dimensions: {
    width: number
    height: number
  }
  rooms: Room[]
  constraints: {
    budget?: number
    style?: string
    floors?: number
    special_requirements?: string[]
  }
}

const roomTypes = [
  { value: 'living', label: 'Living Room', icon: '🛋️' },
  { value: 'bedroom', label: 'Bedroom', icon: '🛏️' },
  { value: 'kitchen', label: 'Kitchen', icon: '🍳' },
  { value: 'bathroom', label: 'Bathroom', icon: '🚿' },
  { value: 'office', label: 'Office', icon: '💼' },
  { value: 'dining', label: 'Dining Room', icon: '🍽️' },
  { value: 'storage', label: 'Storage', icon: '📦' },
  { value: 'garage', label: 'Garage', icon: '🚗' },
]

const buildingTypes = [
  { value: 'residential', label: 'Residential', description: 'Home and living spaces' },
  { value: 'commercial', label: 'Commercial', description: 'Office and retail spaces' },
  { value: 'mixed', label: 'Mixed Use', description: 'Combined residential and commercial' },
]

const steps = [
  { id: 'basic', title: 'Basic Info', icon: Home },
  { id: 'dimensions', title: 'Dimensions', icon: Ruler },
  { id: 'rooms', title: 'Rooms', icon: Plus },
  { id: 'constraints', title: 'Constraints', icon: Settings },
  { id: 'review', title: 'Review', icon: Check },
]

export default function NewPlanPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [planData, setPlanData] = useState<PlanData>({
    name: '',
    building_type: 'residential',
    dimensions: { width: 10, height: 8 },
    rooms: [],
    constraints: {}
  })

  const [isGenerating, setIsGenerating] = useState(false)

  const updatePlanData = (updates: Partial<PlanData>) => {
    setPlanData(prev => ({ ...prev, ...updates }))
  }

  const addRoom = () => {
    const newRoom: Room = {
      id: Date.now().toString(),
      name: '',
      type: 'living',
      min_area: 10,
      max_area: 30,
      requirements: []
    }
    updatePlanData({ rooms: [...planData.rooms, newRoom] })
  }

  const updateRoom = (roomId: string, updates: Partial<Room>) => {
    updatePlanData({
      rooms: planData.rooms.map(room => 
        room.id === roomId ? { ...room, ...updates } : room
      )
    })
  }

  const removeRoom = (roomId: string) => {
    updatePlanData({
      rooms: planData.rooms.filter(room => room.id !== roomId)
    })
  }

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    try {
      setIsGenerating(true)
      
      // Transform frontend data to backend format
      const backendRequest: FloorPlanRequest = {
        name: planData.name,
        dimensions: planData.dimensions,
        building_type: planData.building_type,
        constraints: planData.constraints,
        rooms: planData.rooms.map(room => ({
          type: room.type as any, // Cast to RoomType
          area: (room.min_area + room.max_area) / 2, // Use average area
          preferred_width: Math.sqrt((room.min_area + room.max_area) / 2), // Square approximation
          preferred_depth: Math.sqrt((room.min_area + room.max_area) / 2),
          adjacency: [], // TODO: Add adjacency logic if needed
          requirements: room.requirements
        }))
      }

      console.log('Sending plan generation request:', backendRequest)
      
      // Call backend API
      const response = await apiClient.generatePlan(backendRequest)
      
      if (response.plan_id) {
        // Redirect to plan detail page to show progress
        router.push(`/plans/${response.plan_id}`)
      } else {
        throw new Error('No plan ID returned from backend')
      }
      
    } catch (error) {
      console.error('Failed to generate plan:', error)
      // Show error to user
      alert(`Failed to generate plan: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const isStepValid = () => {
    switch (steps[currentStep].id) {
      case 'basic':
        return planData.name.trim() !== '' && planData.building_type
      case 'dimensions':
        return planData.dimensions.width > 0 && planData.dimensions.height > 0
      case 'rooms':
        return planData.rooms.length > 0 && planData.rooms.every(room => 
          room.name.trim() !== '' && room.min_area > 0 && room.max_area > room.min_area
        )
      case 'constraints':
        return true // Constraints are optional
      case 'review':
        return true // Review is just for confirmation
      default:
        return false
    }
  }

  const renderStepContent = () => {
    switch (steps[currentStep].id) {
      case 'basic':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Plan Name
              </label>
              <input
                type="text"
                value={planData.name}
                onChange={(e) => updatePlanData({ name: e.target.value })}
                className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                placeholder="e.g., Modern Family Home"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Building Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {buildingTypes.map((type) => (
                  <div
                    key={type.value}
                    className={`
                      p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 relative
                      ${planData.building_type === type.value 
                        ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/40 text-blue-700 dark:text-blue-200 shadow-md ring-2 ring-blue-500/20 dark:ring-blue-400/30' 
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:shadow-sm'
                      }
                    `}
                    onClick={() => updatePlanData({ building_type: type.value as any })}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-medium">{type.label}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                      </div>
                      {planData.building_type === type.value && (
                        <div className="bg-blue-500 dark:bg-blue-400 text-white rounded-full p-1">
                          <Check className="w-4 h-4" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )

      case 'dimensions':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Building Dimensions (meters)
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">Width</label>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updatePlanData({ 
                        dimensions: { ...planData.dimensions, width: Math.max(1, planData.dimensions.width - 1) }
                      })}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <input
                      type="number"
                      value={planData.dimensions.width}
                      onChange={(e) => updatePlanData({ 
                        dimensions: { ...planData.dimensions, width: parseFloat(e.target.value) || 0 }
                      })}
                      className="w-20 px-3 py-2 border border-input rounded-md text-center"
                      min="1"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updatePlanData({ 
                        dimensions: { ...planData.dimensions, width: planData.dimensions.width + 1 }
                      })}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">Height</label>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updatePlanData({ 
                        dimensions: { ...planData.dimensions, height: Math.max(1, planData.dimensions.height - 1) }
                      })}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <input
                      type="number"
                      value={planData.dimensions.height}
                      onChange={(e) => updatePlanData({ 
                        dimensions: { ...planData.dimensions, height: parseFloat(e.target.value) || 0 }
                      })}
                      className="w-20 px-3 py-2 border border-input rounded-md text-center"
                      min="1"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updatePlanData({ 
                        dimensions: { ...planData.dimensions, height: planData.dimensions.height + 1 }
                      })}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Total area: {planData.dimensions.width * planData.dimensions.height} m²
              </p>
            </div>

            <div className="bg-primary/10 border border-primary/20 p-4 rounded-lg">
              <h4 className="font-medium text-primary mb-2">Dimension Guidelines</h4>
              <ul className="text-sm text-foreground space-y-1">
                <li>• Residential: Typically 8-15m wide, 10-20m deep</li>
                <li>• Commercial: Often 15-30m wide, 20-40m deep</li>
                <li>• Consider lot size and local regulations</li>
              </ul>
            </div>
          </div>
        )

      case 'rooms':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">Rooms Configuration</h3>
              <Button onClick={addRoom} className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Add Room</span>
              </Button>
            </div>

            {planData.rooms.length === 0 ? (
              <div className="text-center py-8 border-2 border-dashed border-border rounded-lg">
                <p className="text-muted-foreground">No rooms added yet. Click "Add Room" to get started.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {planData.rooms.map((room, index) => (
                  <Card key={room.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">Room {index + 1}</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeRoom(room.id)}
                          className="text-destructive hover:text-destructive/80"
                        >
                          <Minus className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-foreground mb-1">
                            Room Name
                          </label>
                          <input
                            type="text"
                            value={room.name}
                            onChange={(e) => updateRoom(room.id, { name: e.target.value })}
                            className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                            placeholder="e.g., Master Bedroom"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-foreground mb-1">
                            Room Type
                          </label>
                          <select
                            value={room.type}
                            onChange={(e) => updateRoom(room.id, { type: e.target.value })}
                            className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                          >
                            {roomTypes.map(type => (
                              <option key={type.value} value={type.value}>
                                {type.icon} {type.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-foreground mb-1">
                            Min Area (m²)
                          </label>
                          <input
                            type="number"
                            value={room.min_area}
                            onChange={(e) => updateRoom(room.id, { min_area: parseFloat(e.target.value) || 0 })}
                            className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                            min="1"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-foreground mb-1">
                            Max Area (m²)
                          </label>
                          <input
                            type="number"
                            value={room.max_area}
                            onChange={(e) => updateRoom(room.id, { max_area: parseFloat(e.target.value) || 0 })}
                            className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                            min={room.min_area}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )

      case 'constraints':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Budget (optional)
              </label>
              <input
                type="number"
                value={planData.constraints.budget || ''}
                onChange={(e) => updatePlanData({ 
                  constraints: { ...planData.constraints, budget: parseFloat(e.target.value) || undefined }
                })}
                className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                placeholder="e.g., 150000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Architectural Style
              </label>
              <select
                value={planData.constraints.style || ''}
                onChange={(e) => updatePlanData({ 
                  constraints: { ...planData.constraints, style: e.target.value }
                })}
                className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
              >
                <option value="">No preference</option>
                <option value="modern">Modern</option>
                <option value="traditional">Traditional</option>
                <option value="contemporary">Contemporary</option>
                <option value="minimalist">Minimalist</option>
                <option value="industrial">Industrial</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Number of Floors
              </label>
              <input
                type="number"
                value={planData.constraints.floors || ''}
                onChange={(e) => updatePlanData({ 
                  constraints: { ...planData.constraints, floors: parseInt(e.target.value) || undefined }
                })}
                className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                min="1"
                max="5"
                placeholder="e.g., 2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Special Requirements
              </label>
              <textarea
                value={planData.constraints.special_requirements?.join(', ') || ''}
                onChange={(e) => updatePlanData({ 
                  constraints: { 
                    ...planData.constraints, 
                    special_requirements: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                  }
                })}
                className="w-full px-3 py-2 border-2 border-input bg-background text-foreground font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400"
                rows={3}
                placeholder="e.g., wheelchair accessible, home office, outdoor space"
              />
              <p className="text-sm text-muted-foreground mt-1">Separate multiple requirements with commas</p>
            </div>
          </div>
        )

      case 'review':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium">Review Your Plan</h3>
            
            <div className="bg-muted p-6 rounded-lg space-y-4">
              <div>
                <h4 className="font-medium text-foreground">Plan Details</h4>
                <dl className="mt-2 grid grid-cols-1 gap-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Name:</dt>
                    <dd className="font-medium">{planData.name}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Building Type:</dt>
                    <dd className="font-medium capitalize">{planData.building_type}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Dimensions:</dt>
                    <dd className="font-medium">{planData.dimensions.width}m × {planData.dimensions.height}m</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Total Area:</dt>
                    <dd className="font-medium">{planData.dimensions.width * planData.dimensions.height} m²</dd>
                  </div>
                </dl>
              </div>

              {planData.rooms.length > 0 && (
                <div>
                  <h4 className="font-medium text-foreground">Rooms ({planData.rooms.length})</h4>
                  <ul className="mt-2 space-y-1 text-sm">
                    {planData.rooms.map((room, index) => (
                      <li key={room.id} className="flex justify-between">
                        <span>{index + 1}. {room.name || 'Unnamed Room'}</span>
                        <span className="text-muted-foreground">
                          {roomTypes.find(t => t.value === room.type)?.label} • {room.min_area}-{room.max_area}m²
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {planData.constraints.budget && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Budget:</span>
                  <span className="font-medium">${planData.constraints.budget.toLocaleString()}</span>
                </div>
              )}

              {planData.constraints.style && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Style:</span>
                  <span className="font-medium capitalize">{planData.constraints.style}</span>
                </div>
              )}

              {planData.constraints.floors && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Floors:</span>
                  <span className="font-medium">{planData.constraints.floors}</span>
                </div>
              )}
            </div>

            <div className="bg-primary/10 border border-primary/20 p-4 rounded-lg">
              <h4 className="font-medium text-primary mb-2">Ready to Generate</h4>
              <p className="text-sm text-foreground">
                Click "Generate Plan" to start the AI-powered floor plan generation process. 
                This typically takes 2-5 minutes depending on the complexity.
              </p>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button variant="ghost" onClick={() => window.history.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Create New Plan</h1>
          <p className="text-muted-foreground">Design your custom floor plan with AI assistance</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors
                ${index === currentStep 
                  ? 'bg-primary text-primary-foreground' 
                  : index < currentStep 
                    ? 'bg-success text-success-foreground' 
                    : 'bg-muted text-muted-foreground'
                }
              `}>
                {index < currentStep ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <step.icon className="w-5 h-5" />
                )}
              </div>
              <span className={`
                ml-2 text-sm font-medium hidden sm:block
                ${index === currentStep ? 'text-primary' : 'text-muted-foreground'}
              `}>
                {step.title}
              </span>
              {index < steps.length - 1 && (
                <div className={`
                  w-12 h-0.5 ml-2 hidden sm:block
                  ${index < currentStep ? 'bg-success' : 'bg-muted'}
                `} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep].title}</CardTitle>
          <CardDescription>
            {currentStep === 0 && "Let's start with the basic information about your floor plan."}
            {currentStep === 1 && "Define the overall dimensions of your building."}
            {currentStep === 2 && "Configure the rooms you want in your floor plan."}
            {currentStep === 3 && "Set any additional constraints or preferences."}
            {currentStep === 4 && "Review your plan details before generation."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Previous
        </Button>

        <div className="flex items-center space-x-2">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`
                w-2 h-2 rounded-full
                ${index === currentStep ? 'bg-primary' : 'bg-muted'}
              `}
            />
          ))}
        </div>

        {currentStep === steps.length - 1 ? (
          <Button
            onClick={handleSubmit}
            disabled={!isStepValid()}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Generate Plan</span>
          </Button>
        ) : (
          <Button
            onClick={nextStep}
            disabled={!isStepValid()}
          >
            Next
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  )
}