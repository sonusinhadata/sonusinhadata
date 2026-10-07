from pathlib import Path
from datetime import date
import json
import html

INPUT = Path("data/contributions.json")
OUTPUT = Path("sonu-heatmap.svg")

WIDTH = 900
HEIGHT = 300

CELL = 12
GAP = 4

LEFT = 45
TOP = 65

COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing {INPUT}. Run fetch_contributions.py first."
    )

data = json.loads(INPUT.read_text(encoding="utf-8"))

days = data.get("days", [])
stats = data.get("stats", {})
username = data.get("username", "github")

if not days:
    raise RuntimeError("No contribution data found.")

# Convert contribution data into a date -> level dictionary
contribution_map = {}

for item in days:
    contribution_date = item.get("date")
    level = int(item.get("level", 0))

    if contribution_date:
        contribution_map[contribution_date] = max(0, min(level, 4))


# Use the most recent 364 days = 52 weeks
today = date.today()

dates = []

for offset in range(363, -1, -1):
    current_date = today.fromordinal(today.toordinal() - offset)
    dates.append(current_date)


# Align the first day to Sunday
first_date = dates[0]

while first_date.weekday() != 6:
    first_date = first_date.fromordinal(first_date.toordinal() - 1)

calendar_dates = []

current = first_date

while current <= today:
    calendar_dates.append(current)
    current = current.fromordinal(current.toordinal() + 1)


# Group into weeks
weeks = []

for i in range(0, len(calendar_dates), 7):
    week = calendar_dates[i:i + 7]

    if len(week) == 7:
        weeks.append(week)


# Keep only the latest 52 weeks
weeks = weeks[-52:]


# Calculate actual contribution cells
active_days = sum(
    1 for d in dates
    if contribution_map.get(d.isoformat(), 0) > 0
)


svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

# Background
svg.append(
    f'<rect width="{WIDTH}" height="{HEIGHT}" '
    f'rx="16" fill="#0d1117"/>'
)


# Title
svg.append(
    f'<text x="30" y="32" '
    f'font-family="monospace" font-size="18" '
    f'font-weight="bold" fill="#39d353">'
    f'@{html.escape(username)} — contribution activity'
    f'</text>'
)


# Day labels
day_labels = [
    ("Mon", 1),
    ("Wed", 3),
    ("Fri", 5),
]

for label, row in day_labels:
    y = TOP + row * (CELL + GAP) + 10

    svg.append(
        f'<text x="10" y="{y}" '
        f'font-family="monospace" font-size="10" '
        f'fill="#8b949e">{label}</text>'
    )


# Month labels
previous_month = None

for column, week in enumerate(weeks):

    first_day = week[0]

    month = first_day.strftime("%b")

    if month != previous_month:

        x = LEFT + column * (CELL + GAP)

        svg.append(
            f'<text x="{x}" y="{TOP - 12}" '
            f'font-family="monospace" font-size="10" '
            f'fill="#8b949e">{month}</text>'
        )

        previous_month = month


# Contribution cells
animation_index = 0

for column, week in enumerate(weeks):

    for row, current_date in enumerate(week):

        date_string = current_date.isoformat()

        level = contribution_map.get(date_string, 0)

        x = LEFT + column * (CELL + GAP)
        y = TOP + row * (CELL + GAP)

        delay = animation_index * 0.008

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" '
            f'rx="3" '
            f'fill="{COLORS[level]}">'
            f'<title>{date_string} — level {level}</title>'
            f'<animate '
            f'attributeName="opacity" '
            f'from="0" to="1" '
            f'dur="0.25s" '
            f'begin="{delay:.3f}s" '
            f'fill="freeze"/>'
            f'</rect>'
        )

        animation_index += 1


# Legend
legend_y = TOP + 7 * (CELL + GAP) + 22

svg.append(
    f'<text x="{LEFT}" y="{legend_y}" '
    f'font-family="monospace" font-size="10" '
    f'fill="#8b949e">Less</text>'
)

legend_x = LEFT + 35

for level in range(5):

    x = legend_x + level * (CELL + GAP)

    svg.append(
        f'<rect x="{x}" y="{legend_y - 10}" '
        f'width="{CELL}" height="{CELL}" '
        f'rx="3" fill="{COLORS[level]}"/>'
    )

svg.append(
    f'<text x="{legend_x + 5 * (CELL + GAP) + 5}" '
    f'y="{legend_y}" '
    f'font-family="monospace" font-size="10" '
    f'fill="#8b949e">More</text>'
)


# Stats
stats_y = HEIGHT - 35

longest_streak = stats.get("longest_streak", 0)
current_streak = stats.get("current_streak", 0)

stats_text = (
    f"Active days: {active_days}    "
    f"Current streak: {current_streak} days    "
    f"Longest streak: {longest_streak} days"
)

svg.append(
    f'<text x="30" y="{stats_y}" '
    f'font-family="monospace" font-size="12" '
    f'fill="#8b949e">'
    f'{html.escape(stats_text)}'
    f'</text>'
)

svg.append("</svg>")


OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)

file_size = OUTPUT.stat().st_size

print()
print("================================")
print("SUCCESS!")
print("================================")
print(f"Created: {OUTPUT}")
print(f"File size: {file_size:,} bytes")
print(f"Weeks rendered: {len(weeks)}")
print(f"Active days: {active_days}")
print(f"Current streak: {current_streak}")
print(f"Longest streak: {longest_streak}")