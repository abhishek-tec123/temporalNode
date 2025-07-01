# """
# Test client for running the single node workflow directly.
# """
# import asyncio
# from temporalio import client
# from workflow import SingleNodeWorkflow
# import json
# import time
# from runner import start_temporal_server
# async def main():

#     start_temporal_server()
#     temporal_client = await client.Client.connect("localhost:7233")

#     result = await temporal_client.execute_workflow(
#         SingleNodeWorkflow,
#         id=f"single-node-workflow-{int(time.time())}",
#         task_queue="call-flow-queue",
#     )

#     print("Workflow result:")
#     print(json.dumps(result, indent=4))

# if __name__ == "__main__":
#     asyncio.run(main())

# with fastapi and worker-----------------------------------------------------------

import time
import json
import asyncio
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from temporalio import client
from workflow import SingleNodeWorkflow
from utils import start_temporal_server, print_temporal_logs
from worker import main as worker_main
from routs import router
import socket

app = FastAPI()
app.include_router(router)

def start_temporal_server_async():
    proc = start_temporal_server()
    print_temporal_logs(proc)

def run_worker():
    # Wait for Temporal server to be available
    while True:
        try:
            with socket.create_connection(("localhost", 7233), timeout=2):
                break
        except OSError:
            print("Waiting for Temporal server to be ready on port 7233...")
            time.sleep(1)
    asyncio.run(worker_main())

def start_worker_async():
    thread = threading.Thread(target=run_worker, daemon=True)
    thread.start()

@app.on_event("startup")
def startup_event():
    start_temporal_server_async()
    start_worker_async()

class WorkflowResponse(BaseModel):
    message: str
    result: dict

@app.post("/run-workflow", response_model=WorkflowResponse)
async def run_workflow():
    # Connect to Temporal server
    temporal_client = await client.Client.connect("localhost:7233")

    # Run workflow
    workflow_id = f"single-node-workflow-{int(time.time())}"
    result = await temporal_client.execute_workflow(
        SingleNodeWorkflow,
        id=workflow_id,
        task_queue="call-flow-queue",
    )

    return {
        "message": f"Workflow {workflow_id} completed successfully.",
        "result": result
    }
