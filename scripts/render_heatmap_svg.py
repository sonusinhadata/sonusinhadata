from pathlib import Path
from datetime import date
import json
import html


# ============================================================
# CONFIGURATION
# ============================================================

INPUT = Path("data/contributions.json")
OUTPUT = Path("sonu-heatmap.svg")

# Compact GitHub-friendly canvas
WIDTH = 860
HEIGHT = 205

# Contribution cell size
CELL = 11
GAP = 3

# Heatmap position
LEFT = 38
TOP = 48

# GitHub-style contribution colors
COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]


# ============================================================
# LOAD CONTRIBUTION DATA
# ============================================================

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing {INPUT}. "
        "Run fetch_contributions.py first."
    )

data = json.loads(
    INPUT.read_text(
        encoding="utf-8"
    )
)

days = data.get("days", [])
stats = data.get("stats", {})
username = data.get(
    "username",
    "github"
)

if not days:
    raise RuntimeError(
        "No contribution data found."
    )


# ============================================================
# CREATE DATE -> CONTRIBUTION LEVEL MAP
# ============================================================

contribution_map = {}

for item in days:

    contribution_date = item.get(
        "date"
    )

    level = int(
        item.get("level", 0)
    )

    if contribution_date:

        contribution_map[
            contribution_date
        ] = max(
            0,
            min(level, 4)
        )


# ============================================================
# BUILD LAST 364 DAYS
# ============================================================

today = date.today()

dates = []

for offset in range(
    363,
    -1,
    -1
):

    current_date = (
        today.fromordinal(
            today.toordinal()
            - offset
        )
    )

    dates.append(
        current_date
    )


# ============================================================
# ALIGN CALENDAR TO SUNDAY
# ============================================================

first_date = dates[0]

while first_date.weekday() != 6:

    first_date = (
        first_date.fromordinal(
            first_date.toordinal()
            - 1
        )
    )


calendar_dates = []

current = first_date

while current <= today:

    calendar_dates.append(
        current
    )

    current = (
        current.fromordinal(
            current.toordinal()
            + 1
        )
    )


# ============================================================
# GROUP DATES INTO WEEKS
# ============================================================

weeks = []

for i in range(
    0,
    len(calendar_dates),
    7
):

    week = calendar_dates[
        i:i + 7
    ]

    if len(week) == 7:

        weeks.append(
            week
        )


# Keep only latest 52 weeks
weeks = weeks[-52:]


# ============================================================
# CALCULATE ACTIVE DAYS
# ============================================================

active_days = sum(
    1
    for current_date in dates
    if contribution_map.get(
        current_date.isoformat(),
        0
    ) > 0
)


# ============================================================
# START SVG
# ============================================================

svg = []

svg.append(
    f'<svg '
    f'xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" '
    f'height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)


# ============================================================
# BACKGROUND
# ============================================================

svg.append(
    f'<rect '
    f'width="{WIDTH}" '
    f'height="{HEIGHT}" '
    f'rx="16" '
    f'fill="#0d1117"/>'
)


# ============================================================
# TITLE
# ============================================================

svg.append(
    f'<text '
    f'x="30" '
    f'y="32" '
    f'font-family="monospace" '
    f'font-size="18" '
    f'font-weight="bold" '
    f'fill="#39d353">'
    f'@{html.escape(username)} '
    f'— contribution activity'
    f'</text>'
)


# ============================================================
# DAY LABELS
# ============================================================

day_labels = [
    ("Mon", 1),
    ("Wed", 3),
    ("Fri", 5),
]

for label, row in day_labels:

    y = (
        TOP
        + row * (CELL + GAP)
        + 10
    )

    svg.append(
        f'<text '
        f'x="10" '
        f'y="{y}" '
        f'font-family="monospace" '
        f'font-size="10" '
        f'fill="#8b949e">'
        f'{label}'
        f'</text>'
    )


# ============================================================
# MONTH LABELS
# ============================================================

previous_month = None

for column, week in enumerate(
    weeks
):

    first_day = week[0]

    month = first_day.strftime(
        "%b"
    )

    if month != previous_month:

        x = (
            LEFT
            + column * (CELL + GAP)
        )

        svg.append(
            f'<text '
            f'x="{x}" '
            f'y="{TOP - 12}" '
            f'font-family="monospace" '
            f'font-size="10" '
            f'fill="#8b949e">'
            f'{month}'
            f'</text>'
        )

        previous_month = month


# ============================================================
# CONTRIBUTION CELLS
# ============================================================

animation_index = 0

for column, week in enumerate(
    weeks
):

    for row, current_date in enumerate(
        week
    ):

        date_string = (
            current_date.isoformat()
        )

        level = contribution_map.get(
            date_string,
            0
        )

        x = (
            LEFT
            + column * (CELL + GAP)
        )

        y = (
            TOP
            + row * (CELL + GAP)
        )

        delay = (
            animation_index
            * 0.008
        )

        svg.append(
            f'<rect '
            f'x="{x}" '
            f'y="{y}" '
            f'width="{CELL}" '
            f'height="{CELL}" '
            f'rx="3" '
            f'fill="{COLORS[level]}">'
            f'<title>'
            f'{date_string} '
            f'— level {level}'
            f'</title>'
            f'<animate '
            f'attributeName="opacity" '
            f'from="0" '
            f'to="1" '
            f'dur="0.25s" '
            f'begin="{delay:.3f}s" '
            f'fill="freeze"/>'
            f'</rect>'
        )

        animation_index += 1


# ============================================================
# LEGEND
# ============================================================

legend_y = (
    TOP
    + 7 * (CELL + GAP)
    + 18
)

svg.append(
    f'<text '
    f'x="{LEFT}" '
    f'y="{legend_y}" '
    f'font-family="monospace" '
    f'font-size="10" '
    f'fill="#8b949e">'
    f'Less'
    f'</text>'
)

legend_x = LEFT + 35

for level in range(5):

    x = (
        legend_x
        + level * (CELL + GAP)
    )

    svg.append(
        f'<rect '
        f'x="{x}" '
        f'y="{legend_y - 10}" '
        f'width="{CELL}" '
        f'height="{CELL}" '
        f'rx="3" '
        f'fill="{COLORS[level]}"/>'
    )


svg.append(
    f'<text '
    f'x="{legend_x + 5 * (CELL + GAP) + 5}" '
    f'y="{legend_y}" '
    f'font-family="monospace" '
    f'font-size="10" '
    f'fill="#8b949e">'
    f'More'
    f'</text>'
)


# ============================================================
# STATISTICS
# ============================================================

stats_y = HEIGHT - 18

longest_streak = stats.get(
    "longest_streak",
    0
)

current_streak = stats.get(
    "current_streak",
    0
)

stats_text = (
    f"Active days: {active_days}    "
    f"Current streak: {current_streak} days    "
    f"Longest streak: {longest_streak} days"
)

svg.append(
    f'<text '
    f'x="30" '
    f'y="{stats_y}" '
    f'font-family="monospace" '
    f'font-size="12" '
    f'fill="#8b949e">'
    f'{html.escape(stats_text)}'
    f'</text>'
)


# ============================================================
# CLOSE SVG
# ============================================================

svg.append(
    "</svg>"
)


# ============================================================
# WRITE FILE
# ============================================================

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


# ============================================================
# RESULT
# ============================================================

file_size = OUTPUT.stat().st_size

print()
print("================================")
print("SUCCESS!")
print("================================")
print(
    f"Created: {OUTPUT}"
)
print(
    f"File size: "
    f"{file_size:,} bytes"
)
print(
    f"Weeks rendered: "
    f"{len(weeks)}"
)
print(
    f"Active days: "
    f"{active_days}"
)
print(
    f"Current streak: "
    f"{current_streak}"
)
print(
    f"Longest streak: "
    f"{longest_streak}"
)
print()