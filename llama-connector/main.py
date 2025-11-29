import time
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required, but unused
)


def ask_llm(prompt):
    # print(f"\nUser: {prompt}")
    # print("Assistant: ", end="", flush=True)

    start_time = time.time()
    first_token_received = False

    ttft = 0

    stream = client.chat.completions.create(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=256,
        stream=True
    )

    result = ""

    for chunk in stream:
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


if __name__ == "__main__":
    file = open("text_block", "r")
    prompt = ('You are a master negotiator detecting bluffs. Analyze the statement below for deception or exaggeration.'
              '\nInput Text: \n----------------\n"')+file.read()+('"\n----------------\n\nOutput Rules: '
                                             '\n1. Output strictly: "Decision: [TRUE / BLUFF]".'
                                             '\n2. List the specific linguistic or logical trigger for your decision.'
                                             '\n3. Do not exceed 50 words. Be direct.')
    print(prompt)
    response = ask_llm(prompt)
    outputFile = open("output", "w")
    outputFile.write(response)
    print(response)