#!/bin/bash

cd /home/ishanp/Documents/GitHub/AI-CAD/backend
export PORT=8101
export PYTHONPATH="$PWD/src"

echo "Starting AI-CAD Backend Server..."
echo "==============================="

# Start the server in foreground
python3 -c "
import os
print(f'PORT environment: {os.environ.get(\"PORT\")}')
print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\")}')

from src.main import app
import uvicorn

print('Starting uvicorn server...')
try:
    uvicorn.run(app, host='0.0.0.0', port=8101, log_level='info')
except Exception as e:
    print(f'Error starting server: {e}')
    import traceback
    traceback.print_exc()
"