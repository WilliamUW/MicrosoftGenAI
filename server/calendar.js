import axios from "axios";
import { format } from "path";

const access_token = process.env.GOOGLE_ACCESS_TOKEN;

function formatCalendarEvents(calendarEvents) {
  if (calendarEvents) {
    return calendarEvents.map((event) => {
      try {
        const startTime = event?.start?.dateTime || event?.start?.date;
        const formattedDate = new Date(startTime).toLocaleString();
        const eventName = event.summary;

        return `${formattedDate} - ${eventName}\n`;
      } catch (e) {
        console.log("Broken event: ", event);
      }
    });
  } else {
    return "The user has not connected their calendar. No calendar information available.";
  }
}


async function getGoogleCalendarEvents() {

  var now = new Date();
  var yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const timeMin = yesterday.toISOString();

  const calendarResponse = await axios.get(
    `https://www.googleapis.com/calendar/v3/calendars/primary/events`,
    {
      params: {
        calendarId: id,
        timeMin: timeMin,
        maxResults: 40,
        singleEvents: true,
        orderBy: "startTime",
      },
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    }
  );

  // console.log("calendarResponse: ", calendarResponse);

  var events = calendarResponse.data.items;
  // console.log("Calendar events: ", events);

  return events;
}
