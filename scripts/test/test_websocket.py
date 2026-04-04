#!/usr/bin/env python3

import asyncio
import websockets
import json

async def test_websocket():
    plan_id = "test-plan-123"
    uri = f"ws://localhost:8100/ws/plans/{plan_id}"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe_updates"
            }))
            print("Sent subscription message")
            
            # Wait for messages
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {response}")
            except asyncio.TimeoutError:
                print("No message received in 5 seconds")
            
            # Send ping
            await websocket.send(json.dumps({
                "type": "ping"
            }))
            print("Sent ping")
            
            # Wait for pong
            try:
                pong = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {pong}")
            except asyncio.TimeoutError:
                print("No pong received in 5 seconds")
                
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())