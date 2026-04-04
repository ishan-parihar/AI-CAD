#!/bin/bash

# Quick test script to verify AI-CAD servers are running

echo "Testing AI-CAD servers..."

# Test backend
echo "Testing backend..."
if ss -tln 2>/dev/null | grep -q ":8100 "; then
    echo "✅ Backend is running on port 8100"
else
    echo "❌ Backend is not running on port 8100"
fi

# Test frontend ports
echo "Testing frontend..."
if ss -tln 2>/dev/null | grep -q ":3000 "; then
    echo "✅ Frontend is running on port 3000"
    echo "🌐 Access at: http://localhost:3000"
elif ss -tln 2>/dev/null | grep -q ":3001 "; then
    echo "✅ Frontend is running on port 3001"
    echo "🌐 Access at: http://localhost:3001"
else
    echo "❌ Frontend is not running on ports 3000 or 3001"
fi

# Show all listening ports
echo ""
echo "All listening ports:"
ss -tln 2>/dev/null | grep -E ":300[01]|:8100" || echo "No AI-CAD ports found"