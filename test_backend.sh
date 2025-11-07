#!/bin/bash

echo "Testing AI-CAD Backend on port 8101..."

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s http://localhost:8101/api/v1/health || echo "Health check failed"

echo -e "\n\n2. Testing AI configuration endpoint..."
# Test 2: Get AI config
curl -s http://localhost:8101/api/v1/settings/ai-config || echo "AI config endpoint failed"

echo -e "\n\n3. Testing plan generation..."
# Test 3: Generate a simple plan
curl -X POST http://localhost:8101/api/v1/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Plan",
    "building_type": "residential",
    "dimensions": {"width": 10, "height": 8},
    "rooms": [{"type": "bedroom", "area": 15}],
    "constraints": {}
  }' || echo "Plan generation failed"

echo -e "\n\n4. Listing plans..."
# Test 4: List plans
curl -s http://localhost:8101/api/v1/plans || echo "List plans failed"

echo -e "\n\nTest complete!"