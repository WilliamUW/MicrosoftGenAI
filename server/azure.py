import json
import PIL
from flask import Flask, request, jsonify
from pathlib import Path
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
import base64
import mss
from PIL import Image, ImageGrab
import requests
from dotenv import load_dotenv
import os
import os
import requests
import base64
import asyncio
import time
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()
client = AzureOpenAI(
    azure_endpoint="https://ai-bwilliamwangwestus167464300836.openai.azure.com/",
    api_key=os.getenv("WESTUS_AZURE_API_KEY"),
    api_version="2024-02-15-preview",
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "user_needs_help",
            "description": "Only call this if the user explicitly says 'I need help'. Do not call this function if they are ask for what do you see / what is front of me / what am I holding.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object": {
                        "type": "string",
                        "description": "The object they need help with.",
                    },
                },
                "required": ["object"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_flight_path",
            "description": "Render a flight path if the user has an upcoming flight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA, or a zip code, e.g., 95616.",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_calendar",
            "description": "If the user asks what's upcoming their calendar, check the user's calendar for upcoming events and provide a summary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_eclipse",
            "description": "If the user asks how an eclipse works, render a 3D model of the eclipse.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object": {
                        "type": "string",
                        "description": "The object of interest for the user to visualize.",
                    }
                },
                "required": ["object"],
            },
        },
    },
]

messages = [
    {
        "role": "system",
        "content": "You are GARVIS (Generative Artifical Research Virtual Intelligence System): Leverage augmented reality and visual intelligence to analyze surroundings, provide contextual information, generate interactive 3D models, and assist with real-time decision-making. Operate as an interactive visual assistant that enhances user understanding and interaction in their immediate environment. You will receive what the users sees in front of them and their query. Respond to the user concisely in a few sentences max.",
    },
]


def needVisualContext(prompt):
    start_time = time.time()
    completion = client.chat.completions.create(
        model="gpt-35-turbo",  # model = "deployment_name"
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that will analyze the user's query and decide whether it requires visual context from the user's environment. Respond with 'Yes' if the query pertains to what the user is currently seeing, or 'No' if it does not. Examples of 'No' responses include queries that ask about general knowledge, calendar events, or abstract information. Examples of 'Yes' responses include queries about the user's immediate surroundings, such as 'I need help' or 'What are these'.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    # asyncio.run(azureImageCall("What do you see?", "./test.png"))
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    print(completion)
    message_content = completion.choices[0].message.content
    print(message_content)
    return "Yes" in message_content


def getAzureResponse(userPrompt, imageResponse):
    global messages
    prompt = "User Query: " + userPrompt + ". What the user is seeing: " + imageResponse
    messages.append({"role": "user", "content": prompt})
    print(prompt)
    response = None
    if "eclipse" in prompt or "help" in prompt or "calendar" in prompt:
        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
    else:
        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=messages,
        )
    print(response)
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:

        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            # Parsing the JSON arguments:
            tool_call_arguments = json.loads(tool_call.function.arguments)

            # Extracting the "object" value:
            object_value = tool_call_arguments.get("object", "No object found")

            print("Extracted object:", object_value)

            print("The model wants to call the function: ", function_name, object_value)

            additional_information = ""

            match (function_name):
                case "user_needs_help":
                    additional_information = (
                        "I have rendered a 3d model of the object "
                        + object_value
                        + " you need help with, as well as tutorial video!"
                    )

                case "check_calendar":
                    additional_information = "You have a flight to New York's LaGuardia Airport tomorrow at 8am. I have rendered a 3d map of NYC to better assist your travels including the location of your hotel in Soho, your upcoming meetings at the World Trade Center, and your upcoming dinner in Brooklyn!"

                case "render_eclipse":
                    additional_information = "I have rendered a 3d model of the eclipse for you to visualize."

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": additional_information,
                }
            )  # extend conversation with function response
        # second_response = client.chat.completions.create(
        #     model="gpt-35-turbo",
        #     messages=messages,
        # )
        # print(second_response)
        result = {
            "status": "success",
            "type": "function",
            "function_name": function_name,
            "text": additional_information + " " + imageResponse,
        }
        print(result)
        messages.append(
            {
                "role": "assistant",
                "content": additional_information + " " + imageResponse,
            }
        )
        return result
    else:
        print("The model does not want to call a function", response_message.content)
        result = {
            "status": "success",
            "type": "text",
            "text": response_message.content,
        }
        print(result)
        messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
            }
        )
        return result


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


app = Flask(__name__)


def get_tutorial():
    print("Getting tutorial")


GPT4V_KEY = os.getenv("WESTUS_AZURE_API_KEY")


async def capture_screen(filename="capture.png"):
    with mss.mss() as sct:
        # The screen part to capture
        # Use the first monitor
        monitor = sct.monitors[1]  # Index 1 is the first monitor

        # Capture the screen
        sct_img = sct.shot(mon=monitor, output=filename)

        # Optionally, to convert the raw data captured by mss into a PIL Image:
        # (This step is not necessary if you only need to save it as a file directly)
        img = Image.open(sct_img)
        img.save(filename)

        print(f"Screenshot saved as {filename}")

        return img


@app.route("/data", methods=["GET"])
async def get():
    return (
        jsonify(
            {
                "status": "success",
                "message": "this endpoint is working!",
            }
        ),
        200,
    )


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def azureImageCall(prompt, IMAGE_PATH="./capture.png"):
    # get screenshot
    screenshot = ImageGrab.grab()

    # save screenshot
    screenshot.save("capture.png")
    screenshot.close()
    print("Image captured.")

    # Configuration
    encoded_image = base64.b64encode(open(IMAGE_PATH, "rb").read()).decode("ascii")
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT4V_KEY,
    }

    # Payload for the request
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 100,
        # "tools": tools,
    }

    GPT4V_ENDPOINT = "https://ai-bwilliamwangwestus167464300836.openai.azure.com/openai/deployments/gpt-4vision/chat/completions?api-version=2024-02-15-preview"

    # Send request
    try:
        print("Sending request...")
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed (e.g., print or process)
    response_data = response.json()
    print("Response Data:", response_data)
    message_content = response_data["choices"][0]["message"]["content"]
    print("Message Content:", message_content)
    # print(messages)
    return message_content


@app.route("/data", methods=["POST"])
async def receive_data():
    global chat
    global start_convo
    global messages
    data = request.json
    user_input = data["user_input"]
    print("Data Received:", data)
    print("User input: ", user_input)

    if "reset" in data:
        if data["reset"]:
            print("resetting conversation")
            # TODO
            messages = [
                {
                    "role": "system",
                    "content": "You are GARVIS (Generative Artifical Research Virtual Intelligence System): Leverage augmented reality and visual intelligence to analyze surroundings, provide contextual information, generate interactive 3D models, and assist with real-time decision-making. Operate as an interactive visual assistant that enhances user understanding and interaction in their immediate environment. You will receive what the users sees in front of them and their query. Respond to the user concisely in a few sentences max.",
                },
            ]

    # get screenshot
    screenshot = ImageGrab.grab()

    # save screenshot
    screenshot.save("capture.png")
    screenshot.close()

    image_path = Path("capture.png")
    imageString = image_to_base64(image_path)

    prompt = user_input

    visualContextNeeded = needVisualContext(prompt)

    imageResponse = "None"

    if visualContextNeeded:
        print("Visual context needed")
        imageResponse = await azureImageCall(prompt)
        print(imageResponse)
    else:
        print("Visual context not needed")

    # function call plus visual context
    azureResponse = getAzureResponse(prompt, imageResponse)

    if azureResponse:
        azureResponse["image"] = imageString
        return (
            jsonify(azureResponse),
            200,
        )
    #     function_call = response.parts[0].function_call
    #     function_name = function_call.name
    #     additional_information = ""
    #     match (function_name):
    #         case "user_needs_help":
    #             additional_information = "I have rendered a 3d model of the object you need help with, as well as tutorial video."

    #         case "check_calendar":
    #             additional_information = "The user has a flight to New York's LaGuardia Airport tomorrow at 8am. I have rendered a 3d map of NYC to better assist your travels including the location of your hotel in Soho, your upcoming meetings at the World Trade Center, and your upcoming dinner in Brooklyn."

    #         case "render_eclipse":
    #             additional_information = (
    #                 "I have rendered a 3d model of the eclipse for you to visualize."
    #             )
    #     afterFunctionResponse = chat.send_message(
    #         "Respond to the user that the action has been performed. Additional information: "
    #         + additional_information,
    #         tools=[],
    #     )
    #     print(afterFunctionResponse)

    #     return (
    #         jsonify(
    #             {
    #                 "status": "success",
    #                 "type": "function",
    #                 "function_name": function_name,
    #                 "text": afterFunctionResponse.text,
    #                 "image": imageString,
    #             }
    #         ),
    #         200,
    #     )
    # else:


# async def start():
#     await azureImageCall("What do you see?", "./test.png")


if __name__ == "__main__":
    print("starting server")
    # getAzureResponse("introduce yourself")
    # needVisualContext("whats in front of me?")
    app.run(host="127.0.0.1", port=5000, debug=True)
