#!/usr/bin/env node

// Test the LINE entity parsing fix directly
const DxfParser = require('dxf-parser');

const fs = require('fs');

function testLineParsing() {
    const planId = "471bfe76-0102-4317-ad0b-8634d75cec43";
    const dxfFile = `/home/ishanp/Documents/GitHub/AI-CAD/backend/outputs/${planId}/Anees.dxf`;
    
    console.log(`🔍 Testing LINE entity parsing fix...`);
    
    try {
        const content = fs.readFileSync(dxfFile, 'utf8');
        const parser = new DxfParser();
        const dxf = parser.parseSync(content);
        
        if (dxf && dxf.entities) {
            const lineEntities = dxf.entities.filter(e => e.type === 'LINE');
            console.log(`📊 Found ${lineEntities.length} LINE entities`);
            
            lineEntities.forEach((entity, index) => {
                console.log(`\n--- LINE Entity ${index + 1} ---`);
                console.log(`Raw vertices:`, entity.vertices);
                
                // Simulate the parsing logic from DXFViewer
                let startPoint, endPoint, coordinates;
                
                if (entity.vertices && Array.isArray(entity.vertices) && entity.vertices.length >= 2) {
                    startPoint = [entity.vertices[0].x, entity.vertices[0].y];
                    endPoint = [entity.vertices[1].x, entity.vertices[1].y];
                    coordinates = [startPoint[0], startPoint[1], endPoint[0], endPoint[1]];
                }
                
                console.log(`Parsed startPoint:`, startPoint);
                console.log(`Parsed endPoint:`, endPoint);
                console.log(`Parsed coordinates:`, coordinates);
                
                // Simulate the rendering logic
                let lineStart = startPoint;
                let lineEnd = endPoint;
                
                if (!lineStart && !lineEnd && entity.vertices && Array.isArray(entity.vertices) && entity.vertices.length >= 2) {
                    const vertices = entity.vertices;
                    lineStart = [vertices[0].x, vertices[0].y];
                    lineEnd = [vertices[1].x, vertices[1].y];
                    console.log(`Fallback extraction from vertices:`, { lineStart, lineEnd });
                }
                
                console.log(`Final rendering coordinates:`, { lineStart, lineEnd });
                
                if (lineStart && lineEnd && lineStart.length >= 2 && lineEnd.length >= 2) {
                    console.log(`✅ LINE entity can be rendered successfully`);
                    
                    // Simulate Fabric.js Line creation
                    const scale = 10, offsetX = 50, offsetY = 50;
                    const lineCoords = [
                        lineStart[0] * scale + offsetX,
                        lineStart[1] * scale + offsetY,
                        lineEnd[0] * scale + offsetX,
                        lineEnd[1] * scale + offsetY
                    ];
                    console.log(`Fabric.js Line coordinates:`, lineCoords);
                } else {
                    console.log(`❌ LINE entity rendering failed`);
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

testLineParsing();