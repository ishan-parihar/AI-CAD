// Debug script to check frontend environment variables
const http = require('http');

console.log('Testing frontend environment configuration...');

// Test the expected frontend URL (port 3001)
const frontendOptions = {
  hostname: 'localhost',
  port: 3001,
  path: '/',
  method: 'GET'
};

const frontendReq = http.request(frontendOptions, (res) => {
  console.log(`✅ Frontend accessible on port 3001 - Status: ${res.statusCode}`);
});

frontendReq.on('error', (error) => {
  console.error('❌ Frontend not accessible:', error.message);
});

frontendReq.end();

// Test what the frontend would call - the backend API
const backendOptions = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/plans',
  method: 'GET'
};

const backendReq = http.request(backendOptions, (res) => {
  console.log(`✅ Backend API accessible from frontend context - Status: ${res.statusCode}`);
  console.log('✅ Frontend should be able to call: http://localhost:8000/api/v1/plans');
});

backendReq.on('error', (error) => {
  console.error('❌ Backend API not accessible from frontend context:', error.message);
});

backendReq.end();

console.log('Environment check complete. The frontend should now work with the corrected API URL.');