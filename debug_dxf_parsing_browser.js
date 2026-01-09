// Test script to run in browser console to debug DXF parsing
// Copy and paste this into the browser console on the plan page

async function debugDXFParsing() {
  console.log('🧪 Starting DXF Parsing Debug')
  
  try {
    // Get the DXF file the same way the viewer does
    const planId = '471bfe76-0102-4317-ad0b-8634d75cec43'
    const response = await fetch(`http://localhost:8000/api/v1/plans/${planId}/download?file_format=dxf`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch DXF: ${response.status}`)
    }
    
    const dxfContent = await response.text()
    console.log('✅ DXF content loaded, length:', dxfContent.length)
    
    // Parse with the same library
    const DxfParser = window.DxfParser || (await import('dxf-parser')).default
    const parser = new DxfParser()
    const dxf = parser.parseSync(dxfContent)
    
    console.log('✅ DXF parsed successfully')
    console.log('📊 Total entities:', dxf.entities?.length || 0)
    
    // Analyze first few entities in detail
    dxf.entities?.slice(0, 5).forEach((entity, index) => {
      console.log(`\n🔍 Entity ${index + 1} Detailed Analysis:`)
      console.log('  Type:', entity.type)
      console.log('  Layer:', entity.layer)
      console.log('  All properties:', Object.keys(entity))
      
      // Check for different coordinate properties
      console.log('  vertices:', entity.vertices)
      console.log('  points:', entity.points)  
      console.log('  coordinates:', entity.coordinates)
      console.log('  start point:', entity.startPoint, entity.start)
      console.log('  end point:', entity.endPoint, entity.end)
      console.log('  center:', entity.center)
      console.log('  radius:', entity.radius)
      console.log('  Full entity:', entity)
    })
    
    // Look for LWPOLYLINE specifically
    const lwpolylines = dxf.entities?.filter(e => e.type === 'LWPOLYLINE') || []
    console.log(`\n🔍 Found ${lwpolylines.length} LWPOLYLINE entities`)
    
    if (lwpolylines.length > 0) {
      console.log('First LWPOLYLINE structure:', lwpolylines[0])
    }
    
  } catch (error) {
    console.error('❌ DXF parsing debug failed:', error)
  }
}

// Auto-run the debug
debugDXFParsing()