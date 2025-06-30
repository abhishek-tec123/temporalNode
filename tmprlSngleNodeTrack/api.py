"""
API for running a single node workflow via Temporal and FastAPI.
"""
from fastapi import FastAPI
import json
from pydantic import BaseModel
from llm import on_startup
from temporalio.client import Client
from workflow import SingleNodeWorkflow
from activities import (
    test_node,
    start_call,
    end_call,
    email_sent,
)
from fastapi.responses import JSONResponse
from fastapi import status
import httpx

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    on_startup()

class NodeRequest(BaseModel):
    node_id: str
    inputs: dict = {}

NODE_FLOW_URL = "http://localhost:3000/node_flow.json"

@app.post("/run_single_node")
async def run_single_node(request: NodeRequest):
    async with httpx.AsyncClient() as client:
        response = await client.get(NODE_FLOW_URL)
        response.raise_for_status()
        flow = response.json()
    node = next((n for n in flow["nodes"] if n["uniqueId"] == request.node_id), None)
    if not node:
        return {"message": "Node not found", "result": None}

    # Inject user inputs into node config
    if "config" in node and "properties" in node["config"]:
        node["config"]["properties"].update(request.inputs)
    else:
        node["config"] = {"properties": request.inputs}

    try:
        temporal_client = await Client.connect("localhost:7233")
        result = await temporal_client.execute_workflow(
            SingleNodeWorkflow,
            node,
            id=f"single-node-workflow-{request.node_id}",
            task_queue="call-flow-queue",
        )
        if result.get("status") == "success":
            return result
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": result.get("message", "Activity did not complete successfully."),
                    "result": result,
                    "error_code": "ACTIVITY_FAILED"
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_message": f"Workflow failed: {str(e)}",
                "message": "Try Again"
            }
        )

@app.get("/status")
async def health_check():
    """
    Health check endpoint to verify if the API is running.
    Returns:
        dict: A simple message indicating the API is running
    """
    return {"status": "success", "message": "API is running"}