from pathlib import Path


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

OUTPUT = Path("sonu-info.svg")

WIDTH = 650

ROW_HEIGHT = 48

TOP_MARGIN = 110

LEFT_KEY = 30

LEFT_VALUE = 190


# --------------------------------------------------
# INFORMATION
# --------------------------------------------------

INFO = [
    ("ROLE", "Data Analyst"),
    ("FOCUS", "Business Intelligence"),
    ("STACK", "SQL • Power BI • Excel"),
    ("CODE", "Python • Pandas • DAX"),
    ("TOOLS", "Power Query • Git • GitHub"),
    ("ANALYTICS", "EDA • KPI • Data Modeling"),
    ("CURRENT", "Building Analytics Projects"),
]


# --------------------------------------------------
# CALCULATE SIZE
# --------------------------------------------------

HEIGHT = (
    TOP_MARGIN
    + len(INFO) * ROW_HEIGHT
    + 30
)


# --------------------------------------------------
# START SVG
# --------------------------------------------------

svg = []

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
>

<rect
x="5"
y="5"
width="{WIDTH - 10}"
height="{HEIGHT - 10}"
rx="14"
fill="#0d1117"
stroke="#30363d"
stroke-width="2"
/>

<style>

.title {{
    font-family: monospace;
    font-size: 25px;
    font-weight: bold;
    fill: #39d353;
}}

.subtitle {{
    font-family: monospace;
    font-size: 13px;
    fill: #8b949e;
}}

.key {{
    font-family: monospace;
    font-size: 16px;
    font-weight: bold;
    fill: #69f0a0;
}}

.value {{
    font-family: monospace;
    font-size: 16px;
    fill: #eeeeee;
}}

.row {{
    opacity: 0;
}}

.cursor {{
    fill: #39d353;
}}

</style>


<text
x="30"
y="45"
class="title">
SONU@GITHUB
</text>


<text
x="30"
y="72"
class="subtitle">
Data Analyst • Business Intelligence
</text>


<rect
x="30"
y="88"
width="{WIDTH - 60}"
height="1"
fill="#30363d"
/>
'''
)


# --------------------------------------------------
# ADD INFORMATION ROWS
# --------------------------------------------------

for index, (key, value) in enumerate(INFO):

    y = TOP_MARGIN + index * ROW_HEIGHT

    delay = 0.5 + index * 0.25

    svg.append(
        f'''
<g class="row">

<animate
attributeName="opacity"
from="0"
to="1"
begin="{delay:.2f}s"
dur="0.4s"
fill="freeze"
/>

<text
x="{LEFT_KEY}"
y="{y}"
class="key">
{key}
</text>

<text
x="{LEFT_VALUE}"
y="{y}"
class="value">
{value}
</text>

</g>
'''
    )


# --------------------------------------------------
# CURSOR
# --------------------------------------------------

cursor_y = TOP_MARGIN + len(INFO) * ROW_HEIGHT

svg.append(
    f'''
<rect
x="30"
y="{cursor_y - 17}"
width="8"
height="18"
class="cursor">

<animate
attributeName="opacity"
values="1;0;1"
dur="1s"
repeatCount="indefinite"
/>

</rect>
'''
)


# --------------------------------------------------
# CLOSE SVG
# --------------------------------------------------

svg.append("</svg>")


# --------------------------------------------------
# WRITE FILE
# --------------------------------------------------

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


# --------------------------------------------------
# SUCCESS MESSAGE
# --------------------------------------------------

file_size = OUTPUT.stat().st_size

print()
print("================================")
print("SUCCESS!")
print("================================")
print(f"Created: {OUTPUT}")
print(f"File size: {file_size:,} bytes")
print(f"Dimensions: {WIDTH} x {HEIGHT}")