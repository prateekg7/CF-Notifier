# CFNotify - Codeforces Calendar

A lightweight, serverless tool that generates an auto-updating **iCalendar (.ics)** feed for upcoming Codeforces contests.

**Hosted on GitHub Pages** | **Updates Hourly via GitHub Actions**

---

## How to Subscribe

**[Click Here to Subscribe](https://prateekg7.github.io/CFNotify/)**

This link will take you to a landing page where you can:
- **Add to Apple Calendar** (iPhone/Mac)
- **Add to Google Calendar** (Android/Web)
- **Get the direct .ics URL**

---

## How it Works
1.  **Github Actions** runs `tracker.py` every hour.
2.  The script fetches contests from Codeforces API.
3.  It updates `codeforces.ics` with the latest schedule.
4.  The change is pushed to the repo, and **GitHub Pages** serves the file to your phone's calendar.

---

## Project Structure
- `tracker.py`: logic to fetch API and generate ICS.
- `.github/workflows/update_calendar.yml`: The scheduler (Cron job).
- `index.html`: The landing page for subscribers.
- `codeforces.ics`: The generated calendar file (automatically updated).
