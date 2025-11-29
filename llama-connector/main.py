import time
import asyncio
import os
import json
import boto3
import websockets
import aiomysql

from sus_prompt import get_sus_prompt
from sug_prompt import get_sug_prompt
from fac_prompt import get_fac_prompt
from final_prompt import get_final_prompt
import dbcreds

# Initialize Bedrock Runtime Client
# Region: eu-central-1 (Frankfurt)
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-central-1'
)

# Model ID for Claude 3 Haiku
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# DB Pool
db_pool = None


async def init_db_pool():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=dbcreds.DB_HOST,
        port=dbcreds.DB_PORT,
        user=dbcreds.DB_USER,
        password=dbcreds.DB_PASSWORD,
        db=dbcreds.DB_NAME,
        autocommit=True
    )


async def save_to_db(conv_id, text, author):
    if not db_pool:
        print("DB pool not initialized")
        return

    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Get the last message_id for this conversation
                await cur.execute("SELECT MAX(message_id) FROM dialogs WHERE conv_id = %s", (conv_id,))
                result = await cur.fetchone()
                last_msg_id = result[0] if result[0] is not None else 0
                new_msg_id = last_msg_id + 1

                # Insert the new message
                await cur.execute(
                    "INSERT INTO dialogs (conv_id, message_id, message, author) VALUES (%s, %s, %s, %s)",
                    (conv_id, new_msg_id, text, author)
                )
                print(f"Saved message to DB: conv_id={conv_id}, msg_id={new_msg_id}, author={author}")
    except Exception as e:
        print(f"Error saving to DB: {e}")


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


import sys
import os
# Add parent directory to sys.path to allow importing RAG_helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RAG_helper.processQuery import processQuery

async def process_text(input_text, company_id, author):
    print(f"Processing input from {author}: {input_text[:50]}...")
    
    # Retrieve context from RAG
    context = await asyncio.to_thread(processQuery, input_text, company_id)
    if context:
        print(f"Retrieved context (len={len(context)})")
    else:
        print("No context retrieved")

    # Run all requests in parallel using the same Bedrock client
    results = await asyncio.gather(
        ask_llm(bedrock_runtime, get_sus_prompt(input_text, context, author)),
        ask_llm(bedrock_runtime, get_sug_prompt(input_text, context, author)),
        ask_llm(bedrock_runtime, get_fac_prompt(input_text, context, author))
    )

    response_sus, response_sug, response_fac = results

    # Optional: Save to files (can be kept for debugging or logging)
    # open("output_sus", "w").write(response_sus)
    # open("output_sug", "w").write(response_sug)
    # open("output_fac", "w").write(response_fac)

    max_retries = 3
    final_result_json = None

    for attempt in range(max_retries):
        print(f"Generating final result (Attempt {attempt + 1}/{max_retries})...")
        final_result_list = await asyncio.gather(
            ask_llm(bedrock_runtime, get_final_prompt(input_text, response_sus, response_sug, response_fac, context, author))
        )
        raw_result = final_result_list[0]
        
        try:
            # Attempt to find JSON content if it's wrapped in markdown code blocks
            json_str = raw_result
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            final_result_json = json.loads(json_str)
            
            # Validate keys
            if "MESSAGE_COLOR" in final_result_json and "MESSAGE" in final_result_json:
                print("Successfully parsed JSON response.")
                break
            else:
                print("JSON parsed but missing required keys.")
                final_result_json = None
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {raw_result[:100]}...")
        except Exception as e:
            print(f"Error processing JSON: {e}")
    
    if final_result_json is None:
        print("Failed to generate valid JSON after retries.")
        # Fallback or error response
        final_result_json = {
            "MESSAGE_COLOR": "red",
            "MESSAGE": "Error: Could not generate a valid response."
        }
    
    # open("final_result", "w").write(json.dumps(final_result_json))
    
    return json.dumps(final_result_json)


async def handler(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                conv_id = data.get("conv_id")
                input_text = data.get("text")
                company_id = data.get("company_id", 1) # Default to 1 if not provided
                author = data.get("author", "user") # Default to "user" if not provided
                
                if conv_id is None or input_text is None:
                    print("Invalid message format")
                    continue

                print(f"Received message for conv_id={conv_id}, company_id={company_id}, author={author}")
                
                # Fire-and-forget DB save
                asyncio.create_task(save_to_db(conv_id, input_text, author))
                
                response = await process_text(input_text, company_id, author)
                await websocket.send(response)
                print("Sent response")
                
            except json.JSONDecodeError:
                print("Received invalid JSON")
            except Exception as e:
                print(f"Error handling message: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def main():
    await init_db_pool()
    print("DB Pool initialized")
    print("Starting WebSocket server on port 8767...")
    async with websockets.serve(handler, "0.0.0.0", 8767):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())