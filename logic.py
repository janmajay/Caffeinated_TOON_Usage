import os
import json
import base64
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import toon_format
import tiktoken
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from models import DataPayload, UserProfile, Score, Activity

# Load environment variables from .env file
load_dotenv()

def generate_dummy_data(num_users: int = 5) -> DataPayload:
    users = []
    for i in range(num_users):
        scores = [
            Score(subject=f"Subject_{j}", score=random.uniform(50, 100), date=datetime.now() - timedelta(days=j))
            for j in range(3)
        ]
        activities = [
            Activity(
                id=k,
                name=f"Activity_{k}",
                timestamp=datetime.now() - timedelta(hours=k),
                metadata={"location": "US", "device": "mobile"},
                duration_seconds=random.uniform(60, 3600)
            )
            for k in range(5)
        ]
        user = UserProfile(
            id=i,
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            is_active=random.choice([True, False]),
            roles=["admin", "editor"] if i % 2 == 0 else ["viewer"],
            preferences={"theme": "dark", "notifications": "true"},
            scores=scores,
            activities=activities,
            bio="Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5,
            created_at=datetime.now() - timedelta(days=365),
            updated_at=datetime.now()
        )
        users.append(user)
    
    return DataPayload(users=users)

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

@traceable(name="compare_formats")
def run_comparison(num_users: int = 5, model: str = "gpt-4o"):
    data = generate_dummy_data(num_users)
    data_dict = data.model_dump()
    
    # JSON Serialization
    json_str = json.dumps(data_dict, default=str)
    
    # TOON Serialization
    toon_str = toon_format.encode(data_dict)
    
    # Cost Estimation (GPT-4o pricing: $2.50 / 1M input tokens, $10.00 / 1M output tokens)
    input_cost_per_1k = 0.0025  # $2.50 per 1M = $0.0025 per 1k
    output_cost_per_1k = 0.01   # $10.00 per 1M = $0.01 per 1k
    
    results = {
        "json": {
            "content_preview": json_str[:200] + "...",
            "tokens": 0,  # Will be updated with actual usage
            "cost": 0.0,  # Will be updated with actual usage
            "full_content": json_str,
            "actual_usage": None
        },
        "toon": {
            "content_preview": toon_str[:200] + "...",
            "tokens": 0,  # Will be updated with actual usage
            "cost": 0.0,  # Will be updated with actual usage
            "full_content": toon_str,
            "actual_usage": None
        },
        "savings": {
            "tokens": 0,
            "cost": 0.0,
            "percentage": 0.0
        },
        "api_called": False
    }
    
    # Send requests to OpenAI with LangSmith tracing (only if API key is set)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            # Initialize client here to ensure it picks up current environment variables
            client = wrap_openai(OpenAI())
            
            # JSON Request - Send FULL content
            @traceable(name="json_format_request", metadata={"format": "json"})
            def send_json_request():
                return client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a data parser. Respond with 'Received' only."},
                        {"role": "user", "content": f"Process this JSON data:\n{json_str}"}  # FULL content
                    ],
                    max_tokens=10  # Minimal response to save costs
                )
            
            json_response = send_json_request()
            json_usage = json_response.usage
            json_total_tokens = json_usage.total_tokens
            json_input_tokens = json_usage.prompt_tokens
            json_output_tokens = json_usage.completion_tokens
            json_actual_cost = (json_input_tokens / 1000) * input_cost_per_1k + (json_output_tokens / 1000) * output_cost_per_1k
            
            results["json"]["tokens"] = json_total_tokens
            results["json"]["cost"] = json_actual_cost
            results["json"]["actual_usage"] = {
                "prompt_tokens": json_input_tokens,
                "completion_tokens": json_output_tokens,
                "total_tokens": json_total_tokens
            }
            
            print(f"✅ JSON request sent to OpenAI")
            print(f"   Input tokens: {json_input_tokens}, Output tokens: {json_output_tokens}, Total: {json_total_tokens}")
            
            # TOON Request - Send FULL content
            @traceable(name="toon_format_request", metadata={"format": "toon"})
            def send_toon_request():
                return client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a data parser. The user provides data in TOON format. Respond with 'Received' only."},
                        {"role": "user", "content": f"Process this TOON data:\n{toon_str}"}  # FULL content
                    ],
                    max_tokens=10  # Minimal response to save costs
                )
            
            toon_response = send_toon_request()
            toon_usage = toon_response.usage
            toon_total_tokens = toon_usage.total_tokens
            toon_input_tokens = toon_usage.prompt_tokens
            toon_output_tokens = toon_usage.completion_tokens
            toon_actual_cost = (toon_input_tokens / 1000) * input_cost_per_1k + (toon_output_tokens / 1000) * output_cost_per_1k
            
            results["toon"]["tokens"] = toon_total_tokens
            results["toon"]["cost"] = toon_actual_cost
            results["toon"]["actual_usage"] = {
                "prompt_tokens": toon_input_tokens,
                "completion_tokens": toon_output_tokens,
                "total_tokens": toon_total_tokens
            }
            
            print(f"✅ TOON request sent to OpenAI")
            print(f"   Input tokens: {toon_input_tokens}, Output tokens: {toon_output_tokens}, Total: {toon_total_tokens}")
            
            # Calculate savings
            results["savings"]["tokens"] = json_total_tokens - toon_total_tokens
            results["savings"]["cost"] = json_actual_cost - toon_actual_cost
            results["savings"]["percentage"] = ((json_total_tokens - toon_total_tokens) / json_total_tokens) * 100 if json_total_tokens > 0 else 0
            
            results["api_called"] = True
            
            print(f"\n🎉 Check LangSmith project '{os.getenv('LANGSMITH_PROJECT')}' for both traces!")
            print(f"   Token savings: {results['savings']['tokens']} ({results['savings']['percentage']:.2f}%)")
            print(f"   Cost savings: ${results['savings']['cost']:.6f}")
            
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to tiktoken estimates if API call fails
            json_tokens_est = count_tokens(json_str, model)
            toon_tokens_est = count_tokens(toon_str, model)
            results["json"]["tokens"] = json_tokens_est
            results["json"]["cost"] = (json_tokens_est / 1000) * input_cost_per_1k
            results["toon"]["tokens"] = toon_tokens_est
            results["toon"]["cost"] = (toon_tokens_est / 1000) * input_cost_per_1k
            results["savings"]["tokens"] = json_tokens_est - toon_tokens_est
            results["savings"]["cost"] = results["json"]["cost"] - results["toon"]["cost"]
            results["savings"]["percentage"] = ((json_tokens_est - toon_tokens_est) / json_tokens_est) * 100 if json_tokens_est > 0 else 0
    else:
        # If no API key, use tiktoken estimates
        json_tokens_est = count_tokens(json_str, model)
        toon_tokens_est = count_tokens(toon_str, model)
        results["json"]["tokens"] = json_tokens_est
        results["json"]["cost"] = (json_tokens_est / 1000) * input_cost_per_1k
        results["toon"]["tokens"] = toon_tokens_est
        results["toon"]["cost"] = (toon_tokens_est / 1000) * input_cost_per_1k
        results["savings"]["tokens"] = json_tokens_est - toon_tokens_est
        results["savings"]["cost"] = results["json"]["cost"] - results["toon"]["cost"]
        results["savings"]["percentage"] = ((json_tokens_est - toon_tokens_est) / json_tokens_est) * 100 if json_tokens_est > 0 else 0
            
    return results
