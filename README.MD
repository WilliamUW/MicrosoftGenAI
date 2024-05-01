# Welcome to GARVIS

## Important Note: This application is not standalone.

- It requires Oculus Casting and a local backend to process video feed from the deployed Meta Mixed Reality app.
- You need a PC running the local backend with ngrok, with the main display showing the Oculus Casting tab in full screen.

## Step by step setup

0. Pre-requisites

- Unity
- Meta Quest 3
- Azure AI API Key
- ngrok
- Python

Run commmands:

```
cd server

choco install ngrok

ngrok config add-authtoken <token>

pip install -r requirements.txt
```

1. Create .env file.

You need an **WestUS** Azure API Key with **GPT4 Turbo with Vision + GPT 3.5 Turbo (1106)** Deployed

```
WESTUS_AZURE_API_KEY=d22...564
```

!(https://cdn.discordapp.com/attachments/1234940320408539178/1235329172956516533/azure.PNG?ex=6633f972&is=6632a7f2&hm=988aa3b6bdce864a2da91aae95bc8ad0a4d3b4541e8aed03d842bcad555095f9&)

2. Start local python web server

```
cd server && python azure.py
```

3. Make public with ngrok

In separate terminal in server folder, run:

```
cd server && ngrok http http://127.0.0.1:5000
```

4. Update the endpoint URL in the Meta Quest C# script to the ngrok url.

https://github.com/WilliamUW/GARVIS/blob/135ddc978230c9b48d1adf15321834e65ca73656/Assets/MRTemplateAssets/Scripts/ScreenshotHandler.cs#L44

Note: I run this command so it's set to "trusting-ostrich-measured.ngrok-free.app/data" by default.

```
cd server && ngrok http --domain=trusting-ostrich-measured.ngrok-free.app http://127.0.0.1:5000
```

5. Build and run to Quest 3.

Build "mainScene" to Quest 3.

6. Start Oculus Casting to computer.

Make sure the computer screen is the Oculus Casting screen in full screen.

!(https://cdn.discordapp.com/attachments/1234940320408539178/1235329174332248215/oculuscasting.PNG?ex=6633f972&is=6632a7f2&hm=b032de5e7e6c2aaf21b4c8ef6e51aa5651737eacd5c7340177782ca08dabdc39&)

!(https://cdn.discordapp.com/attachments/1234940320408539178/1235329173619478668/fullscreencasting.png?ex=6633f972&is=6632a7f2&hm=26c6a470b007dc9a37f9d4c55f651ce8532f48ee764cc929449994d126a7ff2b&)

7. Talk to GARVIS by facing your palm up, stop recording your speech by facing your palm down.
