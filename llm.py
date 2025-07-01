"""
LLM and external service utilities (currently only query_document is used).
"""
import httpx

async def query_document(query: str, user_id: str = "cheatsheat5", folder_id: str = "langchainCllm") -> dict:
    url = "http://13.235.73.252:8000/query/"
    payload = {
        "query": query,
        "user_id": user_id,
        "folder_id": folder_id
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()  # Return parsed JSON
    except httpx.RequestError as e:
        return {"status": "error", "message": f"Request failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {e}"}

# Optionally, preload the AsyncClient at startup if you want to reuse it (for advanced optimization)
async_client = httpx.AsyncClient()

def on_startup():
    # This can be called at FastAPI startup to warm up or preload resources
    pass
