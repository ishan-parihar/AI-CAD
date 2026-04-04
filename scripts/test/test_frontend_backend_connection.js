#!/usr/bin/env node

// Test script to verify frontend can connect to backend API
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/plans',
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  }
};

const req = http.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  console.log(`Headers: ${JSON.stringify(res.headers)}`);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('Response length:', data.length);
    console.log('Response preview:', data.substring(0, 200) + '...');
    
    // Parse JSON to verify it's valid
    try {
      const parsed = JSON.parse(data);
      console.log('✅ JSON parsing successful');
      console.log('✅ Number of plans:', parsed.plans ? parsed.plans.length : 0);
    } catch (error) {
      console.log('❌ JSON parsing failed:', error.message);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request failed:', error.message);
});

req.end();