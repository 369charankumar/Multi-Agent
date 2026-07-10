"""
IBM WatsonX IAM token management + chat completion client.
"""
import time
import httpx
from config import IBM_API_KEY, IBM_MODEL_ID, IBM_PROJECT_ID, IBM_URL, IBM_IAM_URL

_token_cache: dict = {"token": None, "expires_at": 0}


async def _get_iam_token() -> str:
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            IBM_IAM_URL,
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": IBM_API_KEY,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"IAM token error {resp.status_code}: {resp.text}")
        data = resp.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 3600))
    return _token_cache["token"]


async def chat(messages: list[dict], system_prompt: str = "") -> str:
    """Send a chat request to IBM WatsonX and return the assistant reply."""
    token = await _get_iam_token()

    payload_messages = []
    if system_prompt:
        payload_messages.append({"role": "system", "content": system_prompt})
    payload_messages.extend(messages)

    # WatsonX /ml/v1/text/chat expects parameters at top level (not nested)
    payload = {
        "model_id": IBM_MODEL_ID,
        "project_id": IBM_PROJECT_ID,
        "messages": payload_messages,
        "max_tokens": 1024,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            IBM_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(f"WatsonX API error {resp.status_code}: {resp.text}")
        data = resp.json()

    # Handle both response shapes
    choices = data.get("choices") or data.get("results") or []
    if choices:
        msg = choices[0]
        # shape 1: {"choices":[{"message":{"content":"..."}}]}
        if isinstance(msg, dict) and "message" in msg:
            return msg["message"]["content"]
        # shape 2: {"choices":[{"generated_text":"..."}]}
        if isinstance(msg, dict) and "generated_text" in msg:
            return msg["generated_text"]
    raise RuntimeError(f"Unexpected WatsonX response shape: {data}")
