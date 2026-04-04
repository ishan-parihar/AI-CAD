#!/usr/bin/env python3

import asyncio
import websockets
import json
import requests
from datetime import datetime

async def test_websocket_with_plan():
    # First create a plan
    plan_data = {
        "name": "Test Plan for WebSocket",
        "width": 10.0,
        "height": 12.0,
        "rooms": [
            {"name": "Living Room", "width": 5.0, "height": 6.0, "x": 1.0, "y": 1.0},
            {"name": "Bedroom", "width": 4.0, "height": 5.0, "x": 7.0, "y": 1.0}
        ],
        "requirements": {
            "min_room_size": 4.0,
            "circulation_space": 1.0,
            "accessibility": False
        }
    }
    
    try:
        print("Creating plan...")
        response = requests.post("http://localhost:8100/api/v1/plans", json=plan_data)
        if response.status_code == 200:
            plan_result = response.json()
            plan_id = plan_result["id"]
            print(f"Plan created with ID: {plan_id}")
        else:
            print(f"Failed to create plan: {response.status_code}")
            return
            
    except Exception as e:
        print(f"Error creating plan: {e}")
        return
    
    # Now test WebSocket
    uri = f"ws://localhost:8100/ws/plans/{plan_id}"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected!")
            
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe_updates"
            }))
            print("Sent subscription message")
            
            # Wait for messages
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"Received: {response}")
            except asyncio.TimeoutError:
                print("No message received in 10 seconds")
            
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_with_plan())