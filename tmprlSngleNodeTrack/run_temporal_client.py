"""
Test client for running the single node workflow directly.
"""
import asyncio
from temporalio import client
from workflow import SingleNodeWorkflow
import json
import time

async def main():
    temporal_client = await client.Client.connect("localhost:7233")

    # Load the flow from node_flow.json
    with open("node_flow.json") as f:
        flow = json.load(f)

    # Find the start node
    start_node = next((node for node in flow["nodes"] if node.get("isStart_node")), None)
    if not start_node:
        print("No start node found in node_flow.json")
        return

    result = await temporal_client.execute_workflow(
        SingleNodeWorkflow,
        start_node,  # Pass the full node dict
        id=f"single-node-workflow-{int(time.time())}",
        task_queue="call-flow-queue",
    )

    print("Workflow result:")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
