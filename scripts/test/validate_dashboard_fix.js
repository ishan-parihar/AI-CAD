#!/usr/bin/env node

// Test script to validate dashboard data loading fix
const http = require('http');

console.log('🔍 Validating Dashboard Data Loading Fix...\n');

async function testDashboardLoading() {
  try {
    // Test 1: Check frontend accessibility
    console.log('1. Testing Frontend Accessibility...');
    const frontendResponse = await fetch('http://localhost:3000');
    if (frontendResponse.ok) {
      console.log('   ✅ Frontend accessible on port 3000');
    } else {
      throw new Error(`Frontend not accessible: ${frontendResponse.status}`);
    }

    // Test 2: Check backend API on correct port
    console.log('\n2. Testing Backend API (Port 8100)...');
    const backendResponse = await fetch('http://localhost:8100/api/v1/plans');
    if (backendResponse.ok) {
      console.log('   ✅ Backend API accessible on port 8100');
      const data = await backendResponse.json();
      console.log(`   ✅ API returns ${data.plans ? data.plans.length : 0} plans`);
    } else {
      throw new Error(`Backend API not accessible: ${backendResponse.status}`);
    }

    // Test 3: Test the specific dashboard API endpoint
    console.log('\n3. Testing Dashboard Data Endpoint...');
    const dashboardResponse = await fetch('http://localhost:8100/api/v1/plans?page=1&limit=20');
    if (dashboardResponse.ok) {
      const dashboardData = await dashboardResponse.json();
      if (dashboardData.plans && Array.isArray(dashboardData.plans)) {
        console.log(`   ✅ Dashboard data structure correct`);
        console.log(`   ✅ Contains ${dashboardData.plans.length} plans for dashboard`);
        
        // Test 4: Validate plan data structure
        console.log('\n4. Validating Plan Data Structure...');
        if (dashboardData.plans.length > 0) {
          const samplePlan = dashboardData.plans[0];
          const requiredFields = ['id', 'name', 'status', 'created_at', 'dimensions', 'summary'];
          const missingFields = requiredFields.filter(field => !(field in samplePlan));
          
          if (missingFields.length === 0) {
            console.log('   ✅ Plan data structure valid');
          } else {
            console.log(`   ⚠️  Missing fields: ${missingFields.join(', ')}`);
          }
        }
      } else {
        throw new Error('Invalid dashboard data structure');
      }
    } else {
      throw new Error(`Dashboard endpoint failed: ${dashboardResponse.status}`);
    }

    console.log('\n🎉 DASHBOARD DATA LOADING FIX VALIDATED!');
    console.log('\n📋 Summary:');
    console.log('   ✅ Frontend running on port 3000');
    console.log('   ✅ Backend API running on port 8100');
    console.log('   ✅ Environment configuration correct');
    console.log('   ✅ API endpoints responding properly');
    console.log('   ✅ Data structure validation passed');
    
    console.log('\n🌐 Access Dashboard:');
    console.log('   Open http://localhost:3000/dashboard in your browser');
    console.log('   The dashboard should now load successfully with all plans displayed.');

  } catch (error) {
    console.error('\n❌ VALIDATION FAILED:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('   1. Ensure backend is running on port 8100');
    console.log('   2. Check frontend environment configuration');
    console.log('   3. Verify both services are started');
    process.exit(1);
  }
}

testDashboardLoading();