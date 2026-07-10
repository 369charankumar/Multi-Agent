"""
Run: python test_connection.py
Tests IBM IAM token fetch and one WatsonX chat call.
"""
import asyncio
from ibm_client import _get_iam_token, chat

async def main():
    print("Step 1: Getting IAM token...")
    token = await _get_iam_token()
    print(f"  Token obtained: {token[:20]}...")

    print("\nStep 2: Sending test chat message...")
    reply = await chat(
        messages=[{"role": "user", "content": "Say 'IBM Legal Aid is working!' and nothing else."}]
    )
    print(f"  Reply: {reply}")
    print("\nAll checks passed!")

asyncio.run(main())
