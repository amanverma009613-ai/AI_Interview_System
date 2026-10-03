from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-astra",
    input="Say: AI Interview System API test successful."
)

print(response.output_text)