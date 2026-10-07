from pathlib import Path
from datetime import date, timedelta
import json
import requests
from bs4 import BeautifulSoup


# ==================================================
# CONFIGURATION
# ==================================================

GITHUB_USERNAME = "sonusinhadata"

OUTPUT = Path("data/contributions.json")

URL = (
    f"https://github.com/users/"
    f"{GITHUB_USERNAME}/contributions"
)


# ==================================================
# FETCH GITHUB CONTRIBUTION CALENDAR
# ==================================================

print(f"Fetching contributions for @{GITHUB_USERNAME}...")
print(f"URL: {URL}")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

print(f"HTTP status: {response.status_code}")


# ==================================================
# PARSE HTML
# ==================================================

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

days = soup.select(
    "td.ContributionCalendar-day"
)

print(
    f"Found {len(days)} contribution cells."
)


if not days:
    raise RuntimeError(
        "No contribution cells were found. "
        "Check the GitHub username."
    )


# ==================================================
# EXTRACT DAILY DATA
# ==================================================

contributions = []

for cell in days:

    date_value = cell.get("data-date")

    level_value = cell.get(
        "data-level",
        "0"
    )

    if not date_value:
        continue

    try:
        level = int(level_value)
    except ValueError:
        level = 0

    # GitHub uses a visually convenient
    # level scale from 0 to 4.
    level = max(
        0,
        min(level, 4)
    )

    contributions.append(
        {
            "date": date_value,
            "level": level
        }
    )


# ==================================================
# SORT BY DATE
# ==================================================

contributions.sort(
    key=lambda x: x["date"]
)


# ==================================================
# BASIC STATISTICS
# ==================================================

total_days = len(contributions)

total_contributions = 0

for item in contributions:

    # Contribution count is not always
    # available in the cell itself, so
    # the heatmap primarily uses level.
    if item["level"] > 0:
        total_contributions += 1


# ==================================================
# CURRENT STREAK
# ==================================================

contribution_dates = {
    item["date"]
    for item in contributions
    if item["level"] > 0
}


today = date.today()

current_streak = 0

check_date = today

while (
    check_date.isoformat()
    in contribution_dates
):

    current_streak += 1

    check_date -= timedelta(days=1)


# ==================================================
# LONGEST STREAK
# ==================================================

longest_streak = 0
running_streak = 0
previous_date = None

for item in contributions:

    if item["level"] == 0:
        running_streak = 0
        previous_date = None
        continue

    current_date = date.fromisoformat(
        item["date"]
    )

    if (
        previous_date is not None
        and current_date
        == previous_date + timedelta(days=1)
    ):
        running_streak += 1

    else:
        running_streak = 1

    longest_streak = max(
        longest_streak,
        running_streak
    )

    previous_date = current_date


# ==================================================
# LEVEL COUNTS
# ==================================================

level_counts = {
    "0": 0,
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0
}

for item in contributions:

    level = str(item["level"])

    level_counts[level] += 1


# ==================================================
# CREATE OUTPUT
# ==================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

result = {
    "username": GITHUB_USERNAME,
    "source": URL,
    "days": contributions,
    "stats": {
        "days": total_days,
        "active_days": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "level_counts": level_counts
    }
}


# ==================================================
# WRITE JSON
# ==================================================

OUTPUT.write_text(
    json.dumps(
        result,
        indent=2
    ),
    encoding="utf-8"
)


# ==================================================
# SUCCESS
# ==================================================

file_size = OUTPUT.stat().st_size

print()
print("================================")
print("SUCCESS!")
print("================================")
print(
    f"Created: {OUTPUT}"
)
print(
    f"File size: {file_size:,} bytes"
)
print(
    f"Contribution cells: {len(contributions)}"
)
print(
    f"Active days: {total_contributions}"
)
print(
    f"Current streak: {current_streak}"
)
print(
    f"Longest streak: {longest_streak}"
)