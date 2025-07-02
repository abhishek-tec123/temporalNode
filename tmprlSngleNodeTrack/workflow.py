"""
Workflow definition for single node execution with Temporal.
"""
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from activities import (
    start_call,
    end_call,
    email_sent,
    sms_sent,
    knowledge_base_call,
    schedule_meeting,
    waiting_for_response,
    api_connectivity,
    http_connectivity,
    webhook_connectivity,
)

activity_map = {
    "startCall": start_call,
    "emailSent": email_sent,
    "smsSent": sms_sent,
    "endCall": end_call,
    "knowledgeBaseCall": knowledge_base_call,
    "scheduleMeeting": schedule_meeting,
    "waitingforResponse": waiting_for_response,
    "apiConnectivity": api_connectivity,
    "http": http_connectivity,
    "webhook": webhook_connectivity,
}

# Define a retry policy for all activities
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=2),      # use timedelta
    backoff_coefficient=2.0,                   # exponential backoff
    maximum_interval=timedelta(seconds=10),    # use timedelta
    maximum_attempts=3                         # total attempts (including the first)
)

@workflow.defn
class SingleNodeWorkflow:
    @workflow.run
    async def run(self, node: dict) -> dict:
        if not node:
            return {"status": "error", "message": "Node not found"}
        inputs = node.get("config", {}).get("properties", {})
        if not any(str(v).strip() for v in inputs.values()):
            return {"status": "no_input", "message": "No user input value for this node."}
        node_type = node["type"]
        activity_func = activity_map.get(node_type)
        if not activity_func:
            return {"status": "error", "message": f"No activity for node type {node_type}"}
        context = {}
        result = await workflow.execute_activity(
            activity_func,
            {"context": context, "inputs": inputs},
            schedule_to_close_timeout=timedelta(seconds=10),
            retry_policy=retry_policy,
        )
        if isinstance(result, dict) and result.get("status") in ["success", "started"]:
            return {
                "status": "success",
                "message": "Activity completed successfully.",
                "activity_result": result.get("message", "Success")
            }
        # Special handling for apiConnectivity, http, and webhook: treat as success if 'response' key exists
        if node_type in ["apiConnectivity", "http", "webhook"] and isinstance(result, dict) and "response" in result:
            return {
                "status": "success",
                "message": f"{node_type} response.",
                "activity_result": result["response"]
            }
        else:
            return {
                "status": "failed",
                "message": "The operation could not be completed after several attempts. Please try again later.",
                "result": None
            }
