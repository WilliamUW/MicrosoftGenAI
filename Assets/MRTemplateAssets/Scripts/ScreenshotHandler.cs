using System.Collections;
using UnityEngine;
using UnityEngine.UI; // Required for UI Button interaction
using TMPro; // Required for TextMeshPro interaction
using System;
using static UnityEngine.Rendering.DebugUI;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Xml;
using System.Threading.Tasks;
using Newtonsoft;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections.Specialized;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using Newtonsoft.Json;
using SimpleJSON; // Make sure to include this
using Meta.Voice.Samples.Dictation;
using System.Reflection;
using Button = UnityEngine.UI.Button;

public class ScreenshotHandler : MonoBehaviour
{
    public DictationActivation controller; // Assign this in the Inspector
    public UnityEngine.UI.Button clearButton;
    public TextMeshProUGUI transcriptionText; // Reference to the TextMeshPro UI component on the button

    public UnityEngine.UI.InputField textToSpeechInputTextField;
    public Button textToSpeechStartButton; // Reference to the UI Button
    public Button textToSpeechStopButton; // Reference to the UI Button

    MethodInfo onClickMethod = typeof(Button).GetMethod("Press", BindingFlags.NonPublic | BindingFlags.Instance);


    public UnityEngine.UI.Button captureButton; // Reference to the UI Button
    public TextMeshProUGUI captureButtonText; // Reference to the TextMeshPro UI component on the button
    public RawImage displayImage;  // Assign this in the inspector
    private List<Dictionary<string, object>> conversation = new List<Dictionary<string, object>>();
    // private string base64String = "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";
    private const string url = "https://trusting-ostrich-measured.ngrok-free.app/data";
    private string user_input = "";
    private string apiKey = "";

    public AudioSource audioSource;    // Reference to the AudioSource component
    public AudioClip[] audioClips;     // Array to hold multiple audio clips
    public List<GameObject> spawnObjects = new List<GameObject>();
    public GameObject tutorialPanel;

    IEnumerator checkInternetConnection(Action<bool> action)
    {
        WWW www = new WWW(url);
        yield return www;
        if (www.error != null)
        {
            updateCaptureButtonText("Status of your endpoint: " + url + " - Not Working. Please check your internet connection, local python backend, ngrok deployment, and url endpoint.");
        }
        else
        {
            updateCaptureButtonText("Status of your endpoint: " + url + " - Working!");
        }
    }
    void Start()
    {
        tutorialPanel.SetActive(true);

        // speak("hi there");
        StartCoroutine(checkInternetConnection((isConnected) =>
        {
            // handle connection status here
        }));
        StartCoroutine(PostData("Introduce yourself as GARVIS to a new user.", true, false));
        // StartCoroutine(PostData("What do you see?", true, false));

        // GeminiImage(base64String);
        // Register the OnButtonPressed function to the button's onClick event
        if (captureButton != null)
        {
            captureButton.onClick.AddListener(OnButtonPressed);
        }
        // Initialize AudioSource component if not assigned
        if (audioSource == null)
        {
            audioSource = GetComponent<AudioSource>();
        }

        // for (int i = 0; i < spawnObjects.Count; i++) {
        //     spawnObject(i);
        // }
    }

    public void spawnObject(int objectIndex)
    {
        if (objectIndex < 0 || objectIndex >= spawnObjects.Count)
        {
            Debug.LogError("Object index out of range.");
            return;
        }
        var newObject = Instantiate(spawnObjects[objectIndex]);
        Vector3 spawnPoint = new Vector3(0, 1, 0);
        newObject.transform.position = spawnPoint;
        // newObject.transform.localScale = new Vector3(1, 1, 1);
    }
    // Function to play an audio clip by index
    public void PlayClip(int clipIndex)
    {
        if (clipIndex < 0 || clipIndex >= audioClips.Length)
        {
            Debug.LogError("Clip index out of range.");
            return;
        }

        // Set the clip and play it
        audioSource.clip = audioClips[clipIndex];
        audioSource.Play();
    }

    private void clickButton(UnityEngine.UI.Button button)
    {
        onClickMethod?.Invoke(button, null);
    }

    public void palmUpEnter()
    {
        Debug.Log("Gesture detected start");
        PlayClip(2);
        onClickMethod?.Invoke(clearButton, null);
        clickButton(textToSpeechStopButton);
        controller.ToggleActivation();
        updateCaptureButtonText("Listening...");

        // OnButtonPressed();
    }

    public void palmUpEnd()
    {
        Debug.Log("Gesture end");
        PlayClip(2);
        user_input = transcriptionText.text;
        Debug.Log(user_input);

        updateCaptureButtonText(user_input);

        StartCoroutine(PostData(user_input));

        // Optionally update the button text when pressed
        if (captureButtonText != null)
        {
            captureButtonText.text = "Asking... " + user_input;
        }


        controller.ToggleActivation();
        // OnButtonPressed();
    }

    public void OnButtonPressed()
    {
        // Start the screenshot capture process
        StartCoroutine(PostData("Describe this image"));

        // Optionally update the button text when pressed
        if (captureButtonText != null)
        {
            captureButtonText.text = "Asking...";
        }
    }

    void updateCaptureButtonText(string text)
    {
        // Update button text after screenshot is displayed
        if (captureButtonText != null)
        {
            captureButtonText.text = text;
        }
    }

    public string TextureToBase64String(Texture2D texture)
    {
        // Convert the texture to a byte array
        byte[] imageBytes = texture.EncodeToPNG();  // You can also use EncodeToJPG()

        // Convert the byte array to a Base64 string
        string base64String = Convert.ToBase64String(imageBytes);

        return base64String;
    }

    void speak(string text)
    {
        PlayClip(2);
        Debug.Log("Speak: " + text);
        textToSpeechInputTextField.text = text;
        onClickMethod?.Invoke(textToSpeechStartButton, null);

    }

    private Texture2D Base64ToTexture(string base64)
    {
        try
        {
            byte[] imageBytes = Convert.FromBase64String(base64);
            Texture2D texture = new Texture2D(2, 2); // Create a new texture (size does not matter)
            if (texture.LoadImage(imageBytes)) // Load the image
            {
                return texture; // If load succeeds, texture size will be replaced by the loaded image
            }
        }
        catch (Exception ex)
        {
            Debug.LogError("Error loading base64 image: " + ex.Message);
        }
        return null;
    }

    IEnumerator PostData(string input, bool reset = false, bool announceQuestion = true)
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            yield break;
        }
        if (announceQuestion)
        {
            speak("I heard: " + input);
        }
        // Example data to send
        string jsonData = $"{{\"user_input\": \"{input}\"}}";
        if (reset)
        {
            jsonData = $"{{\"user_input\": \"{input}\", \"reset\": \"true\"}}";
        }

        // Convert json to bytes
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);

        // Create a new UnityWebRequest with the target URL and method POST
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        // Send the request and wait for the response
        yield return request.SendWebRequest();

        if (request.isNetworkError || request.isHttpError)
        {
            Debug.LogError("Error: " + request.error);
            updateCaptureButtonText("Rate limit, please try again.");
            speak("Rate limit error, please try again.");
        }
        else
        {
            Debug.Log("Response: " + request.downloadHandler.text);
            // Parse JSON to extract the 'message' field
            var N = JSON.Parse(request.downloadHandler.text);
            string message = N["text"];

            // Update button text with the message
            updateCaptureButtonText(message);
            speak(message);

            // Additional log to show the extracted message
            Debug.Log("Extracted Message: " + message);

            string function_name = N["function_name"];
            if (!string.IsNullOrEmpty(function_name))
            {
                switch (function_name)
                {
                    case "check_calendar":
                        spawnObject(3);
                        break;
                    case "user_needs_help":
                        spawnObject(1);
                        tutorialPanel.SetActive(true);
                        break;
                    case "render_eclipse":
                        spawnObject(2);
                        break;
                    default:
                        Debug.Log("Function not recognized: " + function_name);
                        break;
                }
            }

            string base64EncodedImage = N["image"]; // Assuming the field you're looking for is named 'message'
            if (!string.IsNullOrEmpty(base64EncodedImage))
            {
                Texture2D texture = Base64ToTexture(base64EncodedImage);
                if (texture != null && displayImage != null)
                {
                    displayImage.texture = texture;
                }
            }
        }
    }

    IEnumerator CaptureScreenshotAndDisplay()
    {
        // Wait till the end of the frame
        yield return new WaitForEndOfFrame();

        // Capture the screenshot
        Texture2D screenshot = ScreenCapture.CaptureScreenshotAsTexture();

        if (displayImage != null)
        {
            displayImage.texture = screenshot;
        }

        Debug.Log(screenshot);
        Debug.Log("Screenshot dimensions: " + screenshot.width + "x" + screenshot.height);

        string encodedString = TextureToBase64String(screenshot);

        updateCaptureButtonText("encoded string length: " + encodedString.Length);

        Debug.Log(encodedString);
        GeminiImage(encodedString);
    }
    public async void GeminiImage(string base64String)
    {
        updateCaptureButtonText("0");

        var url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent";

        using (HttpClient client = new HttpClient())
        {
            updateCaptureButtonText("0.1");

            client.BaseAddress = new Uri(url);
            var requestUri = $"?key={apiKey}";

            var safetySettings = new List<object>
                {
                    new { category = "HARM_CATEGORY_HARASSMENT", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_HATE_SPEECH", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_DANGEROUS_CONTENT", threshold = "BLOCK_NONE" }
                };

            updateCaptureButtonText("0.2");

            var requestBody = new
            {
                contents = new Dictionary<string, object>
                {
                    { "parts", new List<object>
                        {
                            new { text = "Describe everything you observe in the image with high levels of detail." },
                            new
                            {
                                inlineData = new
                                {
                                    mimeType = "image/png",
                                    data = base64String
                                }
                            }
                        }
                    }
                }
            };
            updateCaptureButtonText(".3");

            var payload = new
            {
                contents = conversation,
                // safetySettings = safetySettings,
            };
            updateCaptureButtonText("1");
            // Serialize the payload
            var conversationJson = JsonConvert.SerializeObject(requestBody, Newtonsoft.Json.Formatting.None);

            updateCaptureButtonText("2");

            HttpContent content = new StringContent(conversationJson, Encoding.UTF8, "application/json");

            try
            {

                updateCaptureButtonText("3 Sending HTTP request...");

                HttpResponseMessage httpresponse = await client.PostAsync(requestUri, content);
                updateCaptureButtonText("4 received");

                httpresponse.EnsureSuccessStatusCode();
                updateCaptureButtonText("5");

                string responseBody = await httpresponse.Content.ReadAsStringAsync();
                updateCaptureButtonText("6");

                Debug.Log(responseBody);

                JObject jsonResponse = JObject.Parse(responseBody);
                updateCaptureButtonText("7");

                Debug.Log(jsonResponse);

                // string extractedText = (string)jsonResponse["candidates"][0]["content"]["parts"][0]["text"];

                // Attempt to extract text directly
                JToken jtokenResponse = jsonResponse["candidates"][0]["content"]["parts"][0]["text"];
                updateCaptureButtonText("8");

                if (jtokenResponse != null)
                {
                    updateCaptureButtonText("9");

                    string extractedText = jtokenResponse.ToString();

                    Debug.Log("Extracted Text: " + extractedText);

                    updateCaptureButtonText(extractedText);

                    if (extractedText != null)
                    {
                        speak(extractedText);
                    }
                }
            }
            catch (HttpRequestException e)
            {
                Debug.Log("\nException Caught!");
                Debug.Log("Message :{0} " + e.Message);
            }
        }
    }

    public async void AskGemini()
    {
        var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent";

        using (HttpClient client = new HttpClient())
        {
            client.BaseAddress = new Uri(url);
            var requestUri = $"?key={apiKey}";

            // Append user response to the conversation history
            conversation.Add(new Dictionary<string, object>
                {
                    { "role", "user" },
                    { "parts", new List<object>
                        {
                            new { text = "tell me a joke" },
                        }
                    }
                });

            Debug.Log(JsonConvert.SerializeObject(conversation, Newtonsoft.Json.Formatting.Indented));
            var safetySettings = new List<object>
                {
                    new { category = "HARM_CATEGORY_HARASSMENT", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_HATE_SPEECH", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold = "BLOCK_NONE" },
                    new { category = "HARM_CATEGORY_DANGEROUS_CONTENT", threshold = "BLOCK_NONE" }
                };

            var functionDeclarations = new
            {
                function_declarations = new[]
                {
                new
                {
                    name = "reset_position",
                    description = "Resets the positions of the planets to their default states in the virtual scene.",
                    parameters = new
                    {
                        type = "object",
                        properties = new { }
                    }
                }
            }
            };


            // Existing objects: conversation and safetySettings

            var requestBody = new
            {
                contents = conversation,
                safetySettings = safetySettings,
                tools = new[]
            {
                new
                {
                    function_declarations = new List<object>
                    {
                        new
                        {
                            name = "change_size",
                            description = "change the size of a planet or star by some magnitude",
                            parameters = new
                            {
                                type = "object",
                                properties = new
                                {
                                    body = new { type = "string", description = "The planet or star. The possible options are The Milky Way, The Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus Neptune, Pluto, Messier-87 Black Hole" },
                                    magnitude = new { type = "number", description = "The magnitude of the size change. E.g. 1.2, 3, 5.2, 10" }
                                },
                                required = new[] { "description" }
                            }
                        },
                    }
                }
            },
                tool_config = new
                {
                    function_calling_config = new
                    {
                        mode = "AUTO"
                    },
                }
            };

            var payload = new
            {
                contents = conversation,
                safetySettings = safetySettings,
            };
            // Serialize the payload
            var conversationJson = JsonConvert.SerializeObject(requestBody, Newtonsoft.Json.Formatting.None);
            HttpContent content = new StringContent(conversationJson, Encoding.UTF8, "application/json");

            try
            {
                HttpResponseMessage httpresponse = await client.PostAsync(requestUri, content);
                httpresponse.EnsureSuccessStatusCode();
                string responseBody = await httpresponse.Content.ReadAsStringAsync();
                Debug.Log(responseBody);

                JObject jsonResponse = JObject.Parse(responseBody);
                Debug.Log(jsonResponse);

                // string extractedText = (string)jsonResponse["candidates"][0]["content"]["parts"][0]["text"];

                // Attempt to extract text directly
                JToken jtokenResponse = jsonResponse["candidates"][0]["content"]["parts"][0]["text"];

                if (jtokenResponse != null)
                {
                    string extractedText = jtokenResponse.ToString();

                    Debug.Log("Extracted Text: " + extractedText);


                    // Parse and handle model response here if necessary
                    // Example: Append model response to the conversation
                    // This is a placeholder. You need to extract actual response from responseBody JSON.
                    conversation.Add(new Dictionary<string, object>
                    {
                        { "role", "model" },
                        { "parts", new List<object>
                            {
                                new { text = extractedText }
                            }
                        }
                    });

                    Debug.Log(JsonConvert.SerializeObject(conversation, Newtonsoft.Json.Formatting.Indented));

                    if (extractedText != null)
                    {
                        speak(extractedText);
                    }
                }
                else
                {
                    // Check if there is a function call
                    JToken functionCall = jsonResponse["candidates"][0]["content"]["parts"][0]["functionCall"];
                    if (functionCall != null)
                    {
                        string functionName = (string)functionCall["name"];
                        JObject args = (JObject)functionCall["args"];

                        // Based on function name, call the relevant method
                        Debug.Log($"Function Call Detected: {functionName}");
                        // ExecuteFunctionCall(functionName, args);
                        //if (functionName == "change_size")
                        //{
                        //    change_size(functionCall["args"]["magnitude"].ToString(), functionCall["args"]["body"].ToString());
                        //}
                    }
                    else
                    {
                        Debug.Log("No valid text or function call found in the response.");
                    }
                }

            }
            catch (HttpRequestException e)
            {
                Debug.Log("\nException Caught!");
                Debug.Log("Message :{0} " + e.Message);
            }
        }
    }
}
