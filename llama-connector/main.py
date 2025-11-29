import time
import asyncio
import os
from openai import AsyncOpenAI

from sus_prompt import get_sus_prompt
from sug_prompt import get_sug_prompt
from fac_prompt import get_fac_prompt
from final_prompt import get_final_prompt

# Client 1 (Default port)
client1 = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Client 2 (Second port for parallelism)
client2 = AsyncOpenAI(
    base_url="http://localhost:11435/v1",
    api_key="ollama"
)

# Client 3 (Third port for parallelism)
client3 = AsyncOpenAI(
    base_url="http://localhost:11436/v1",
    api_key="ollama"
)


async def ask_llm(client, prompt):
    # print(f"\nUser: {prompt}")
    # print("Assistant: ", end="", flush=True)

    start_time = time.time()
    first_token_received = False

    ttft = 0

    try:
        stream = await client.chat.completions.create(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=256,
            stream=True
        )

        result = ""

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content

                if not first_token_received:
                    ttft = (time.time() - start_time) * 1000
                    first_token_received = True
                    print(f" [TTFT: {ttft:.2f}ms] \n", end="")

                result += content;
                # print(content, end="", flush=True)

        print(f" [GEN LATENCY: {(time.time() - start_time - ttft/1000)*1000:.2f}ms] \n", end="")
        print(f" [FULL LATENCY: {(time.time() - start_time)*1000:.2f}ms] \n", end="")
        # print("\n" + "-" * 30)
        return result
    except Exception as e:
        print(f"Error connecting to client {client.base_url}: {e}")
        return ""


async def main():
    input_text = open("text_block", "r").read()

    # Run all requests in parallel using different clients
    results = await asyncio.gather(
        ask_llm(client1, get_sus_prompt(input_text)),
        ask_llm(client2, get_sug_prompt(input_text)),
        ask_llm(client3, get_fac_prompt(input_text))
    )

    response_sus, response_sug, response_fac = results

    open("output_sus", "w").write(response_sus)
    open("output_sug", "w").write(response_sug)
    open("output_fac", "w").write(response_fac)

    result = await asyncio.gather(
        ask_llm(client1, get_final_prompt(input_text, response_sus, response_sug, response_fac))
    )

    open("final_result", "w").write(result[0])


if __name__ == "__main__":
    asyncio.run(main())