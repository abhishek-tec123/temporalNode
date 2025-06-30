"""
API for running a single node workflow via Temporal and FastAPI.
"""
from fastapi import FastAPI, File, UploadFile, Form, Request
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
from fastapi.responses import JSONResponse, FileResponse
from fastapi import status
import httpx
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    on_startup()

class NodeRequest(BaseModel):
    node_id: str
    inputs: dict = {}

NODE_FLOW_DATA = None

@app.post("/upload_node_flow")
async def upload_node_flow(request: Request):
    global NODE_FLOW_DATA
    # Only accept raw JSON
    if not request.headers.get("content-type", "").startswith("application/json"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Only raw JSON body with Content-Type: application/json is supported."}
        )
    try:
        NODE_FLOW_DATA = await request.json()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Invalid JSON body: {str(e)}"}
        )
    return {"message": "Node flow uploaded successfully from raw JSON"}

@app.post("/run_single_node")
async def run_single_node(request: NodeRequest):
    global NODE_FLOW_DATA
    if NODE_FLOW_DATA is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Node flow data not uploaded. Please upload using /upload_node_flow first."}
        )
    node = next((n for n in NODE_FLOW_DATA["nodes"] if n["uniqueId"] == request.node_id), None)
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

@app.get("/node_flow.json")
async def get_node_flow():
    file_path = os.path.join(os.path.dirname(__file__), "node_flow.json")
    return FileResponse(file_path, media_type="application/json")