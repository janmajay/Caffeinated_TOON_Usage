"""
Quick test script to verify LangSmith integration is working.
This will make a simple OpenAI request and you should see it in LangSmith.
"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("Environment Variables:")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"LANGSMITH_API_KEY: {'SET' if os.getenv('LANGSMITH_API_KEY') else 'NOT SET'}")
print(f"LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
print(f"LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
print(f"LANGSMITH_ENDPOINT: {os.getenv('LANGSMITH_ENDPOINT')}")

if os.getenv('OPENAI_API_KEY') and os.getenv('LANGSMITH_API_KEY'):
    print("\n✅ Both API keys are set!")
    print("\nSending test request to OpenAI with LangSmith tracing...")
    
    from openai import OpenAI
    from langsmith.wrappers import wrap_openai
    from langsmith import traceable
    
    client = wrap_openai(OpenAI())
    
    @traceable(name="test_request", metadata={"test": "langsmith_verification"})
    def send_test_request():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'LangSmith integration test successful!' in exactly 5 words."}
            ]
        )
    
    try:
        response = send_test_request()
        print(f"\n✅ Response: {response.choices[0].message.content}")
        print(f"\n🎉 Check LangSmith project '{os.getenv('LANGSMITH_PROJECT')}' for this trace!")
        print(f"   Look for run name: test_request")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Even if there's a LangSmith error, the OpenAI request may still succeed.")
        print("The 403 error might indicate:")
        print("  1. Invalid/expired LANGSMITH_API_KEY")
        print("  2. API key lacks permissions for this project")
        print("  3. Organization/workspace mismatch")
else:
    print("\n❌ Missing API keys. Please set them in .env file.")
