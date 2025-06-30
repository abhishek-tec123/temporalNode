import threading
import asyncio
import uvicorn
import subprocess
import time
import sys
from worker import main as worker_main
from api import app


def start_temporal_server():
    # Start Temporal server in dev mode as a subprocess
    return subprocess.Popen([
        "temporal", "server", "start-dev"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_worker():
    asyncio.run(worker_main())

if __name__ == "__main__":
    # Start the Temporal server
    temporal_proc = start_temporal_server()
    print("Started Temporal server (dev mode) at http://localhost:8233 ... waiting for it to be ready...")
    time.sleep(5)  # Wait a few seconds for the server to be ready

    try:
        # Start the worker in a background thread
        worker_thread = threading.Thread(target=start_worker, daemon=True)
        worker_thread.start()

        # Start the FastAPI server (blocking call)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        # Clean up: terminate the Temporal server process when done
        print("Shutting down Temporal server...")
        temporal_proc.terminate()
        temporal_proc.wait() 