#!/bin/bash

# Dashboard Configuration Validation Script
# This script validates that the frontend and backend are properly configured

echo "🔍 AI-CAD Dashboard Configuration Validator"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation results
VALIDATION_PASSED=true

echo ""
echo "1. Checking Backend Service..."

# Check if backend is running on port 8100
if curl -s http://localhost:8100/api/v1/plans > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Backend API accessible on port 8100${NC}"
    
    # Check if backend returns valid data
    PLAN_COUNT=$(curl -s http://localhost:8100/api/v1/plans | jq -r '.plans | length' 2>/dev/null || echo "0")
    if [ "$PLAN_COUNT" -gt 0 ]; then
        echo -e "   ${GREEN}✅ Backend returns $PLAN_COUNT plans${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Backend accessible but no plans found${NC}"
    fi
else
    echo -e "   ${RED}❌ Backend API not accessible on port 8100${NC}"
    VALIDATION_PASSED=false
fi

echo ""
echo "2. Checking Frontend Configuration..."

# Check if frontend .env.local exists and has correct configuration
if [ -f "frontend/.env.local" ]; then
    echo -e "   ${GREEN}✅ Frontend .env.local file exists${NC}"
    
    # Check API URL configuration
    API_URL=$(grep "NEXT_PUBLIC_API_URL" frontend/.env.local | cut -d'=' -f2)
    if [ "$API_URL" = "http://localhost:8100" ]; then
        echo -e "   ${GREEN}✅ Frontend API URL correctly set to: $API_URL${NC}"
    else
        echo -e "   ${RED}❌ Frontend API URL incorrect: $API_URL (should be http://localhost:8100)${NC}"
        VALIDATION_PASSED=false
    fi
    
    # Check WebSocket URL configuration
    WS_URL=$(grep "NEXT_PUBLIC_WS_URL" frontend/.env.local | cut -d'=' -f2)
    if [ "$WS_URL" = "ws://localhost:8100/ws" ]; then
        echo -e "   ${GREEN}✅ Frontend WebSocket URL correctly set to: $WS_URL${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Frontend WebSocket URL: $WS_URL${NC}"
    fi
else
    echo -e "   ${RED}❌ Frontend .env.local file not found${NC}"
    VALIDATION_PASSED=false
fi

echo ""
echo "3. Checking Frontend Service..."

# Check if frontend is running on port 3000
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Frontend accessible on port 3000${NC}"
else
    echo -e "   ${YELLOW}⚠️  Frontend not accessible on port 3000${NC}"
    echo "      Make sure to run: cd frontend && npm run dev"
fi

echo ""
echo "4. Checking Database Connectivity..."

# Check if backend can connect to database by checking plans endpoint
if curl -s http://localhost:8100/api/v1/plans | jq -e '.plans' > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Database connectivity confirmed${NC}"
else
    echo -e "   ${RED}❌ Database connectivity issue detected${NC}"
    VALIDATION_PASSED=false
fi

echo ""
echo "=========================================="

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
    echo ""
    echo "The dashboard should be fully functional."
    echo "Access it at: http://localhost:3000/dashboard"
else
    echo -e "${RED}❌ VALIDATION FAILED!${NC}"
    echo ""
    echo "Please fix the issues above before accessing the dashboard."
    echo ""
    echo "Common fixes:"
    echo "1. Start the backend: cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8100"
    echo "2. Start the frontend: cd frontend && npm run dev"
    echo "3. Check environment configuration in frontend/.env.local"
    exit 1
fi

echo ""