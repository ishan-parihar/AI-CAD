#!/bin/bash
# Dashboard Fix Validation Script

echo "🔍 Validating Dashboard Loading Fix..."
echo ""

# Test backend health on correct port
echo "1. Testing Backend Health (Port 8100)..."
if curl -s http://localhost:8100/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy on port 8100"
else
    echo "❌ Backend is not responding on port 8100"
    exit 1
fi

# Test plans endpoint
echo ""
echo "2. Testing Plans API Endpoint..."
PLANS_RESPONSE=$(curl -s http://localhost:8100/api/v1/plans)
if [[ $? -eq 0 ]] && [[ "$PLANS_RESPONSE" == *"plans"* ]]; then
    echo "✅ Plans API returning valid data"
    PLAN_COUNT=$(echo "$PLANS_RESPONSE" | grep -o '"id"' | wc -l)
    echo "   Found $PLAN_COUNT plans in database"
else
    echo "❌ Plans API not responding correctly"
    exit 1
fi

# Check frontend configuration
echo ""
echo "3. Validating Frontend Configuration..."
if [[ -f "frontend/.env.local" ]]; then
    API_URL=$(grep "NEXT_PUBLIC_API_URL" frontend/.env.local | cut -d'=' -f2)
    WS_URL=$(grep "NEXT_PUBLIC_WS_URL" frontend/.env.local | cut -d'=' -f2)
    
    if [[ "$API_URL" == *":8100"* ]]; then
        echo "✅ Frontend API URL correctly configured: $API_URL"
    else
        echo "❌ Frontend API URL incorrect: $API_URL (should be port 8100)"
        exit 1
    fi
    
    if [[ "$WS_URL" == *":8100"* ]]; then
        echo "✅ Frontend WebSocket URL correctly configured: $WS_URL"
    else
        echo "❌ Frontend WebSocket URL incorrect: $WS_URL (should be port 8100)"
        exit 1
    fi
else
    echo "❌ Frontend .env.local file not found"
    exit 1
fi

# Test frontend-backend connectivity
echo ""
echo "4. Testing Frontend-Backend Connectivity..."
if curl -s "$API_URL/api/v1/health" > /dev/null 2>&1; then
    echo "✅ Frontend can successfully connect to backend"
else
    echo "❌ Frontend cannot connect to backend at $API_URL"
    exit 1
fi

echo ""
echo "🎉 Dashboard Loading Fix Validation Complete!"
echo "✅ All checks passed - the dashboard should now load correctly"
echo ""
echo "Next steps:"
echo "1. Restart the frontend development server if it's running"
echo "2. Navigate to http://localhost:3000/dashboard"
echo "3. The dashboard should now load plan data successfully"