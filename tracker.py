import logging
import requests
from datetime import datetime, timedelta, timezone
from ics import Calendar, Event

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ICS_FILE = "codeforces.ics"

def get_contests():
    # Grab the public list from Codeforces
    try:
        res = requests.get("https://codeforces.com/api/contest.list?gym=false", timeout=10)
        res.raise_for_status()
        data = res.json()
        if data["status"] == "OK":
            return data["result"]
    except Exception as e:
        logger.error(f"Failed to fetch contests: {e}")
    return []

def main():
    logger.info("Checking for new contests...")
    data = get_contests()
    
    # We only care about future events
    upcoming = [c for c in data if c["phase"] == "BEFORE"]
    logger.info(f"Found {len(upcoming)} upcoming contests.")

    cal = Calendar()
    cal.creator = "CFNotify"

    for c in upcoming:
        # Codeforces gives timestamps in seconds
        start = datetime.fromtimestamp(c["startTimeSeconds"], tz=timezone.utc)
        end = start + timedelta(seconds=c["durationSeconds"])
        
        # Create the event
        e = Event()
        e.name = f"CF: {c['name']}"
        e.begin = start
        e.end = end
        e.uid = f"CF_{c['id']}@codeforces.com" # Stable ID so updates don't duplicate
        e.description = f"Link: https://codeforces.com/contest/{c['id']}"
        e.url = f"https://codeforces.com/contest/{c['id']}"
        
        cal.events.add(e)

    # Save to file
    with open(ICS_FILE, 'w') as f:
        ics_data = str(cal)
        
        # This adds a 1-day and 1-hour alert to every event.
        alarms = """BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Contest tomorrow!
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Contest in 1 hour!
END:VALARM
END:VEVENT"""
        
        # Inject alarms into every event
        final_ics = ics_data.replace("END:VEVENT", alarms)
        f.write(final_ics)
        
    logger.info("Calendar updated!")

if __name__ == "__main__":
    main()
