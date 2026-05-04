from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="my-master-key",
)

resp = client.chat.completions.create(
    model="local-llama3.2",
    messages=[
        {"role": "user", "content": "Write a short haiku about distributed systems."},
    ],
)

print(resp.choices[0].message.content)
