"""
Temporal worker for single node workflow.
"""
import logging
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import SingleNodeWorkflow
import activities

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="call-flow-queue",
        workflows=[SingleNodeWorkflow],
        activities=[
            activities.test_node,
            activities.start_call,
            activities.end_call,
            activities.email_sent,
            activities.sms_sent,
            activities.knowledge_base_call,
            activities.schedule_meeting,
            activities.waiting_for_response,
            activities.api_connectivity,
        ],
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
