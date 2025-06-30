"""
Activity implementations for Temporal workflows.
"""
import asyncio
from temporalio import activity
import logging
import json

logger = logging.getLogger(__name__)

@activity.defn
async def test_node(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[test_node] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (test_node)")
    activity.logger.info("Running test node checks...")
    logger.info(f"[test_node] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    result = {
        "status": "success",
        "message": "Test node completed.",
        "context": context
    }
    logger.info(f"[test_node] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def start_call(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[start_call] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (start_call)")
    caller = inputs.get('caller')
    if not caller:
        raise Exception("Caller ID is missing in start_call node input!")
    activity.logger.info(f"Call started for {caller}")
    logger.info(f"[start_call] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    context["caller_id"] = caller
    result = {
        "status": "started",
        "message": f"Call started for {caller}",
        "context": context
    }
    logger.info(f"[start_call] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def end_call(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[end_call] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (end_call)")
    caller_id = context.get("caller_id")
    if not caller_id:
        raise Exception("Caller ID is missing in end_call node input!")
    activity.logger.info("Ending call.")
    logger.info(f"[end_call] Start | context: {json.dumps(context, indent=4)}")
    await asyncio.sleep(1)
    result = {
        "status": "ended",
        "message": f"Call ended for {context.get('caller_id')}",
        "context": context
    }
    logger.info(f"[end_call] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def email_sent(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[email_sent] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (email_sent)")
    recipient = inputs.get("recipient", "unknown@example.com")
    subject = inputs.get("title", "No Subject")
    description = inputs.get("description", "No Description")
    activity.logger.info(f"Sending email to {recipient} with subject: {subject}")
    logger.info(f"[email_sent] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    result = {
        "status": "success",
        "message": f"Email sent to {recipient} with subject: {subject}",
        "context": context
    }
    logger.info(f"[email_sent] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def sms_sent(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[sms_sent] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (sms_sent)")
    phone_number = inputs.get("phone_number")
    message = inputs.get("message")
    if not phone_number or not message:
        raise Exception("phone_number and message are required for sms_sent activity!")
    activity.logger.info(f"Sending SMS to {phone_number} with message: {message}")
    logger.info(f"[sms_sent] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    result = {
        "status": "success",
        "message": f"SMS sent to {phone_number} with message: {message}",
        "context": context
    }
    logger.info(f"[sms_sent] Result: {json.dumps(result, indent=4)}")
    return result
