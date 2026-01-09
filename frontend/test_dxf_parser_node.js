#!/usr/bin/env node

// Test dxf-parser library directly to see how it handles LINE entities
const DxfParser = require('dxf-parser');

const fs = require('fs');

function testDxfParser() {
    const planId = "471bfe76-0102-4317-ad0b-8634d75cec43";
    const dxfFile = `/home/ishanp/Documents/GitHub/AI-CAD/backend/outputs/${planId}/Anees.dxf`;
    
    console.log(`🔍 Testing dxf-parser with plan: ${planId}`);
    
    try {
        const content = fs.readFileSync(dxfFile, 'utf8');
        console.log(`📄 DXF content length: ${content.length}`);
        
        const parser = new DxfParser();
        const dxf = parser.parseSync(content);
        
        console.log(`🔍 Parsed DXF successfully`);
        console.log(`   Total entities: ${dxf.entities ? dxf.entities.length : 0}`);
        
        if (dxf.entities) {
            dxf.entities.forEach((entity, index) => {
                console.log(`\n--- Entity ${index + 1} ---`);
                console.log(`Type: ${entity.type}`);
                console.log(`Layer: ${entity.layer}`);
                
                if (entity.type === 'LINE') {
                    console.log(`🎯 LINE entity details:`);
                    console.log(`   Raw entity object:`, JSON.stringify(entity, null, 2));
                    
                    // Check all possible coordinate properties
                    const coordProps = ['coordinates', 'startPoint', 'endPoint', 'vertices', 'points', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'start', 'end'];
                    
                    coordProps.forEach(prop => {
                        if (entity.hasOwnProperty(prop)) {
                            console.log(`   ${prop}:`, entity[prop]);
                        }
                    });
                    
                    // Check the prototype chain
                    console.log(`   Entity prototype:`, Object.getPrototypeOf(entity));
                    console.log(`   Entity keys:`, Object.keys(entity));
                    console.log(`   Entity all properties:`, Object.getOwnPropertyNames(entity));
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Error parsing DXF:', error);
    }
}

testDxfParser();