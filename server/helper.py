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

# Load environment variables from .env file
load_dotenv()


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


app = Flask(__name__)


def get_tutorial():
    print("Getting tutorial")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

tool_config = {"function_calling_config": {"mode": "auto"}}
gemini_pro_model = genai.GenerativeModel("gemini-pro")

model = genai.GenerativeModel(
    "gemini-pro",
    tools=[
        {
            "function_declarations": [
                {
                    "name": "user_needs_help",
                    "description": "if the user says I need help, or needs help with anything, help them by finding relevant tutorials for them",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "object": {
                                "type": "string",
                                "description": "the object they need help with",
                            },
                        },
                        "required": ["description"],
                    },
                },
                {
                    "name": "render_flight_path",
                    "description": "render flight path if the user has an upcoming flight",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA or a zip code e.g. 95616",
                            },
                        },
                        "required": ["location"],
                    },
                },
                {
                    "name": "check_calendar",
                    "description": "check the user's calendar for upcoming events and provide a summary",
                },
                {
                    "name": "render_eclipse",
                    "description": "Explain the eclipse if the user mentions the eclipse and render a 3d model of the eclipse",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "object": {
                                "type": "string",
                                "description": "The object of interest for the user to visualize",
                            },
                        },
                        "required": ["object"],
                    },
                },
            ]
        }
    ],
    tool_config=tool_config,
)


global start_convo
start_convo = [
    {
        "role": "user",
        "parts": [
            "You are GARVIS (Gemini Assisted Research Virtual Intelligence System): Leverage augmented reality and visual intelligence to analyze surroundings, provide contextual information, generate interactive 3D models, and assist with real-time decision-making. Operate as an interactive visual assistant that enhances user understanding and interaction in their immediate environment. You will receive what the users sees in front of them and their query. Respond to the user concisely in a few sentences max."
        ],
    },
    {
        "role": "model",
        "parts": ["Ok, I am now GARVIS."],
    },
]
global chat
chat = model.start_chat(history=start_convo, enable_automatic_function_calling=True)


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def imagePathToBase64String(imagePath):
    # Path to the image file
    image_path = Path(imagePath)

    # Read the image file as bytes
    image_bytes = image_path.read_bytes()

    # Encode the bytes to a Base64 string
    base64_bytes = base64.b64encode(image_bytes)

    # Decode the Base64 bytes to a string for use in JSON or other text-based formats
    base64_string = base64_bytes.decode("utf-8")

    print(base64_string)

    return base64_string


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
                "message": "hi",
            }
        ),
        200,
    )


@app.route("/data", methods=["POST"])
async def receive_data():
    global chat
    global start_convo
    data = request.json
    user_input = data["user_input"]
    print("Data Received:", data)
    print("User input: ", user_input)

    if "reset" in data:
        if data["reset"]:
            print("resetting conversation")
            chat = model.start_chat(
                history=start_convo, enable_automatic_function_calling=True
            )

    # get screenshot
    screenshot = ImageGrab.grab()

    # save screenshot
    screenshot.save("capture.png")
    screenshot.close()

    image_path = Path("capture.png")
    imageString = image_to_base64(image_path)

    image_description = "No image description."  # visionResponse.text

    prompt = user_input

    needVisualContextResponse = gemini_pro_model.generate_content(
        "User Query: "
        + prompt
        + ". Analyze the user's query and decide whether it requires visual context from the user's environment. Respond with 'Yes' if the query pertains to what the user is currently seeing, or 'No' if it does not. Examples of 'No' responses include queries that ask about general knowledge, calendar events, or abstract information. Examples of 'Yes' responses include queries about the user's immediate surroundings, such as 'What am I looking at?' or 'What's in front of me?'."
    )
    needVisualContextResponse.resolve()
    print(needVisualContextResponse)

    if needVisualContextResponse and "Yes" in needVisualContextResponse.text:
        # make gemini vision call
        print("Need visual context!")
        visionResponse = await geminiImageCall("Describe in detail what you see.")
        image_description = visionResponse.text
        prompt = (
            "User reply: "
            + user_input
            + ". Only if relevant to their reply, use this description of what the user is seeing: "
            + image_description
        )
    else:
        print("No visual context needed!")
    response = chat.send_message(prompt)

    print(chat.history)
    print(response)
    if response.parts[0].function_call:
        function_call = response.parts[0].function_call
        function_name = function_call.name
        additional_information = ""
        match (function_name):
            case "user_needs_help":
                additional_information = "I have rendered a 3d model of the object you need help with, as well as tutorial video."

            case "check_calendar":
                additional_information = "The user has a flight to New York's LaGuardia Airport tomorrow at 8am. I have rendered a 3d map of NYC to better assist your travels including the location of your hotel in Soho, your upcoming meetings at the World Trade Center, and your upcoming dinner in Brooklyn."

            case "render_eclipse":
                additional_information = (
                    "I have rendered a 3d model of the eclipse for you to visualize."
                )
        afterFunctionResponse = chat.send_message(
            "Respond to the user that the action has been performed. Additional information: "
            + additional_information,
            tools=[],
        )
        print(afterFunctionResponse)

        return (
            jsonify(
                {
                    "status": "success",
                    "type": "function",
                    "function_name": function_name,
                    "text": afterFunctionResponse.text,
                    "image": imageString,
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "status": "success",
                    "type": "text",
                    "text": response.text,
                    "image": imageString,
                }
            ),
            200,
        )


async def start():
    genai.configure(api_key=GOOGLE_API_KEY)
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)

    response = await geminiImageCall("Describe in detail what you see?", "test.png")
    print(response)


async def geminiImageCall(prompt, imageName="capture.png"):
    visionmodel = genai.GenerativeModel("gemini-pro-vision")

    img = PIL.Image.open(imageName)

    response = visionmodel.generate_content([prompt, img])
    response.resolve()
    print(response)

    if hasattr(response, "text"):
        print(response.text)
    else:
        print("error", response)
        response.text = (
            "Sorry, I have been rate-limited, give me 20 seconds to recover!"
        )
    return response


if __name__ == "__main__":
    # start()
    app.run(host="127.0.0.1", port=5000, debug=True)
