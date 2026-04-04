#!/usr/bin/env node

// Simulate browser environment
global.window = {
  location: {
    protocol: 'http:',
    hostname: 'localhost'
  }
};

global.WebSocket = require('ws');

// Set environment variable
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8101';

// Import and test the WebSocket logic
const WebSocket = require('ws');

function testWebSocketConnection() {
  const planId = 'test-plan-browser-sim';
  
  // Simulate the frontend logic
  const wsProtocol = global.window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8101';
  const wsHost = apiBaseUrl.replace(/^https?:\/\//, '');
  const wsUrl = `${wsProtocol}//${wsHost}/ws/plans/${planId}`;
  
  console.log('🧪 Browser Environment WebSocket Test');
  console.log('=======================================');
  console.log(`API Base URL: ${apiBaseUrl}`);
  console.log(`WebSocket URL: ${wsUrl}`);
  console.log(`Protocol: ${wsProtocol}`);
  console.log(`Host: ${wsHost}`);
  console.log('');
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('✅ WebSocket connected successfully!');
    
    // Send subscription message
    const subscribeMsg = {
      type: 'subscribe_updates'
    };
    ws.send(JSON.stringify(subscribeMsg));
    console.log(`📤 Sent: ${JSON.stringify(subscribeMsg)}`);
  });
  
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      console.log(`📥 Received: ${JSON.stringify(message, null, 2)}`);
    } catch (e) {
      console.log(`📥 Received (raw): ${data}`);
    }
  });
  
  ws.on('error', (error) => {
    console.error('❌ WebSocket error:', error);
    console.error('Error details:', error.message);
  });
  
  ws.on('close', (code, reason) => {
    console.log(`🔌 WebSocket closed. Code: ${code}, Reason: ${reason}`);
    
    if (code === 1000) {
      console.log('✅ Normal closure');
    } else {
      console.log(`⚠️  Abnormal closure code: ${code}`);
    }
  });
  
  // Close after 10 seconds
  setTimeout(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.close(1000, 'Test complete');
    }
    process.exit(0);
  }, 10000);
}

// Test HTTP endpoints first
async function testHTTP() {
  const http = require('http');
  
  console.log('1. Testing HTTP endpoints...');
  
  try {
    const healthResponse = await fetch('http://localhost:8101/api/v1/health');
    const healthData = await healthResponse.json();
    console.log(`✅ Health: ${JSON.stringify(healthData)}`);
    
    const aiConfigResponse = await fetch('http://localhost:8101/api/v1/settings/ai-config');
    const aiConfigData = await aiConfigResponse.json();
    console.log(`✅ AI Config: ${JSON.stringify(aiConfigData)}`);
    
    console.log('\n2. Testing WebSocket connection...');
    testWebSocketConnection();
    
  } catch (error) {
    console.error('❌ HTTP test failed:', error);
    process.exit(1);
  }
}

testHTTP();