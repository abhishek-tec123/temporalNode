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


@activity.defn
async def knowledge_base_call(args: dict) -> dict:
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    query = inputs.get("query", "No query provided")
    if not query:
        raise Exception("Query is missing in knowledge_base_call node input!")
    activity.logger.info(f"Querying knowledge base with: {query}")
    logger.info(f"[knowledge_base_call] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    from llm import query_document
    response = await query_document(query)
    # context["last_result"] = response
    result = {
        "status": "success",
        "query": query,
        "result": response,
        "context": context
    }
    logger.info(f"[knowledge_base_call] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def schedule_meeting(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[schedule_meeting] Attempt: {attempt}")
    if inputs.get("force_fail"):
        raise Exception("Forced failure for retry test (schedule_meeting)")
    email = inputs.get("email")
    date = inputs.get("date")
    time_ = inputs.get("time")
    summary = inputs.get("summary")
    if not all([email, date, time_, summary]):
        raise Exception("All fields (email, date, time, summary) are required for schedule_meeting activity!")
    activity.logger.info(f"Scheduling meeting for {email} on {date} at {time_} with summary: {summary}")
    logger.info(f"[schedule_meeting] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    result = {
        "status": "success",
        "message": f"Meeting scheduled for {email} on {date} at {time_} with summary: {summary}",
        "context": context
    }
    logger.info(f"[schedule_meeting] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def waiting_for_response(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[waiting_for_response] Attempt: {attempt}")
    key = inputs.get("key")
    wait_seconds = int(inputs.get("wait_seconds", 5))
    if not key:
        raise Exception("A 'key' input is required for waiting_for_response activity!")
    activity.logger.info(f"Waiting for response with key: {key} for {wait_seconds} seconds")
    logger.info(f"[waiting_for_response] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(wait_seconds)
    result = {
        "status": "success",
        "message": f"Waited for response with key: {key} for {wait_seconds} seconds.",
        "context": context
    }
    logger.info(f"[waiting_for_response] Result: {json.dumps(result, indent=4)}")
    return result

@activity.defn
async def api_connectivity(args: dict) -> dict:
    attempt = activity.info().attempt
    context = args.get("context", {})
    inputs = args.get("inputs", {})
    logger.info(f"[api_connectivity] Attempt: {attempt}")
    api_response = inputs.get("api_response")
    if api_response is None:
        raise Exception("An 'api_response' input is required for api_connectivity activity!")
    activity.logger.info(f"API Connectivity node received response: {api_response}")
    logger.info(f"[api_connectivity] Start | context: {json.dumps(context, indent=4)}, inputs: {json.dumps(inputs, indent=4)}")
    await asyncio.sleep(1)
    return {"response": api_response}