#!/usr/bin/env python3
"""Minimal test server to isolate the issue"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Minimal test server running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting minimal server on port 8101...")
    uvicorn.run(app, host="0.0.0.0", port=8101, log_level="info")