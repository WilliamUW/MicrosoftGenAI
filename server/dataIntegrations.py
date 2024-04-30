import datetime
import os
from googleapiclient.discovery import build


def getYoutubeVideo(search_term):
    # Set up the YouTube Data API v3 client
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)

    # Make the API request to search for videos
    search_response = (
        youtube.search()
        .list(
            q=search_term,
            part="id",
            maxResults=1,
        )
        .execute()
    )

    # Extract the video IDs from the search response
    video_id = search_response["items"][0]["id"]["videoId"]

    # Get the link from the video ID
    video_link = f"https://www.youtube.com/watch?v={video_id}"

    print(video_link)

    return video_link


def googleSearch(search_term):
    # Set up the Google Search API client
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    service = build("customsearch", "v1", developerKey=api_key)

    # Make the API request to search for results
    search_response = (
        service.cse()
        .list(
            q=search_term,
            cx=search_engine_id,
            num=5,
        )
        .execute()
    )

    # Extract the search results from the response
    results = search_response["items"]

    # Extract the title and link for each search result
    for result in results:
        title = result["title"]
        link = result["link"]

        # Print or process the title and link as needed
        print(f"Title: {title}")
        print(f"Link: {link}")

    return results


def getGoogleCalendarEvents():
    # Set up the Google Calendar API client
    api_key = os.getenv("GOOGLE_API_KEY")
    calendar_id = os.getenv("CALENDAR_ID")
    service = build("calendar", "v3", developerKey=api_key)

    # Make the API request to get the list of events
    events_response = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=datetime.datetime.utcnow().isoformat() + "Z",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    # Extract the events from the response
    events = events_response.get("items", [])

    # Process the events as needed
    for event in events:
        event_summary = event["summary"]
        event_start = event["start"].get("dateTime", event["start"].get("date"))
        event_end = event["end"].get("dateTime", event["end"].get("date"))

        # Print or process the event information as needed
        print(f"Summary: {event_summary}")
        print(f"Start: {event_start}")
        print(f"End: {event_end}")

    return events
