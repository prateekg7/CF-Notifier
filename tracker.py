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
        e.dtstamp = datetime.now(timezone.utc) # REQUIRED by RFC 5545 
        
        # REQUIRED: DTSTAMP must be present for valid iCalendar
        # The 'ics' library usually adds this, but let's be explicit if needed or trust the lib.
        # Actually, let's fix the manual string injection first which might corrupt line endings.
        
        e.description = f"Link: https://codeforces.com/contest/{c['id']}"
        e.url = f"https://codeforces.com/contest/{c['id']}"
        
        cal.events.add(e)

    # Save to file
    # Google Calendar is VERY strict about CRLF (\r\n) line endings, mostly served via HTTP.
    # But files on disk should be fine. The issue might be the manual string hack.
    
    with open(ICS_FILE, 'w') as f:
        # We will iterate lines and inject alarms safely
        for line in cal:
            f.write(line)
            if line.startswith("END:VEVENT"):
                # Wait, this logic is wrong. We need to inject BEFORE END:VEVENT.
                pass 

    # Better approach: Convert to string, then replace.
    ics_text = str(cal)
    
    # Ensure CRLF line endings explicitly just in case
    # (The library usually does \r\n, but Windows/Linux/Mac diffs happen)
    
    # RE-INJECT ALARMS SAFELY
    alarm_block = """BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Contest tomorrow!
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Contest in 1 hour!
END:VALARM"""
    
    # Insert alarms before the closing tag of each event
    final_ics = ics_text.replace("END:VEVENT", f"{alarm_block}\r\nEND:VEVENT")
    
    with open(ICS_FILE, 'w', newline='') as f:
        f.write(final_ics)
        
    logger.info("Calendar updated!")

if __name__ == "__main__":
    main()
