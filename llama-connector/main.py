import time
import asyncio
import os
import json
import boto3

from sus_prompt import get_sus_prompt
from sug_prompt import get_sug_prompt
from fac_prompt import get_fac_prompt
from final_prompt import get_final_prompt

# Initialize Bedrock Runtime Client
# Region: eu-central-1 (Frankfurt)
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-central-1'
)

# Model ID for Claude 3 Haiku
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


async def ask_llm(client, prompt):
    # print(f"\nUser: {prompt}")
    # print("Assistant: ", end="", flush=True)

    start_time = time.time()
    ttft = 0 # TTFT is harder to measure precisely without streaming, but we can measure total latency

    # Construct the payload for Claude 3
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.0
    })

    try:
        # Run the synchronous boto3 call in a separate thread to avoid blocking the event loop
        response = await asyncio.to_thread(
            client.invoke_model,
            body=body,
            modelId=MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )

        response_body = json.loads(response.get('body').read())
        result = response_body.get('content')[0].get('text')
        
        # print(result, end="", flush=True)

        print(f" [GEN LATENCY: {(time.time() - start_time - ttft/1000)*1000:.2f}ms] \n", end="")
        print(f" [FULL LATENCY: {(time.time() - start_time)*1000:.2f}ms] \n", end="")
        # print("\n" + "-" * 30)
        return result

    except Exception as e:
        print(f"Error invoking Bedrock model: {e}")
        return ""


async def main():
    input_text = open("text_block1", "r").read()

    # Run all requests in parallel using the same Bedrock client
    # boto3 clients are thread-safe, so we can share the client instance
    results = await asyncio.gather(
        ask_llm(bedrock_runtime, get_sus_prompt(input_text)),
        ask_llm(bedrock_runtime, get_sug_prompt(input_text)),
        ask_llm(bedrock_runtime, get_fac_prompt(input_text))
    )

    response_sus, response_sug, response_fac = results

    open("output_sus", "w").write(response_sus)
    open("output_sug", "w").write(response_sug)
    open("output_fac", "w").write(response_fac)

    result = await asyncio.gather(
        ask_llm(bedrock_runtime, get_final_prompt(input_text, response_sus, response_sug, response_fac))
    )

    open("final_result", "w").write(result[0])


if __name__ == "__main__":
    asyncio.run(main())