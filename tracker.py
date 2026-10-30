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
        # Stable UID is good
        e.uid = f"CF_{c['id']}@codeforces.com" 
        
        # REQUIRED by RFC 5545: DTSTAMP/CREATED
        now = datetime.now(timezone.utc)
        e.dtstamp = now
        e.created = now
        e.last_modified = now
        
        e.description = f"Link: https://codeforces.com/contest/{c['id']}"
        e.url = f"https://codeforces.com/contest/{c['id']}"
        
        cal.events.add(e)

    # Save to file
    ics_text = cal.serialize()
    
    # RE-INJECT ALARMS SAFELY with RFC 5545 CRLF line endings
    alarm_block = (
        "BEGIN:VALARM\r\n"
        "TRIGGER:-P1D\r\n"
        "ACTION:DISPLAY\r\n"
        "DESCRIPTION:Contest tomorrow!\r\n"
        "END:VALARM\r\n"
        "BEGIN:VALARM\r\n"
        "TRIGGER:-PT1H\r\n"
        "ACTION:DISPLAY\r\n"
        "DESCRIPTION:Contest in 1 hour!\r\n"
        "END:VALARM"
    )

    # Insert alarms before the closing tag of each event
    final_ics = ics_text.replace("END:VEVENT", f"{alarm_block}\r\nEND:VEVENT")
    if not final_ics.endswith("\r\n"):
        final_ics += "\r\n"

    with open(ICS_FILE, 'w', newline='') as f:
        f.write(final_ics)
        
    logger.info("Calendar updated!")

if __name__ == "__main__":
    main()
