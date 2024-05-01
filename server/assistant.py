import os
import time
import json
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("ASSISTANT_AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("ASSISTANT_AZURE_OPENAI_ENDPOINT"),
)

assistant = client.beta.assistants.create(
    instructions="",
    model="gpt-4-1106",  # replace with model deployment name.
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Determine weather in my location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state e.g. Seattle, WA",
                        },
                        "unit": {"type": "string", "enum": ["c", "f"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ],
)

# Create a thread
thread = client.beta.threads.create()

while 1:

    # Add a user question to the thread
    user_input = input("Enter your question: ")
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )

    # Run the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )

    # Looping until the run completes or fails
    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    print(run)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(messages)
    elif run.status == "requires_action":
        # the assistant requires calling some functions
        # and submit the tool outputs back to the run
        pass
    else:
        print(run.status)
