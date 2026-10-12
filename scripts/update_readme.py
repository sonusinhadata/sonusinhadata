"""Rewrites the project table and roadmap in README.md from data/progress.json."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DATA = ROOT / "data" / "progress.json"

BADGE = {
    "done": "https://img.shields.io/badge/Completed-15803d?style=flat-square",
    "progress": "https://img.shields.io/badge/In_progress-1d4ed8?style=flat-square",
    "planned": "https://img.shields.io/badge/Planned-64748b?style=flat-square",
}


def projects_table(projects):
    lines = ["| Project | Business question | Tools | Status |", "|---|---|---|---|"]
    for p in projects:
        tools = ", ".join(p["tools"])
        lines.append(f"| [**{p['name']}**]({p['url']}) | {p['question']} | {tools} | ![]({BADGE[p['status']]}) |")
    return "\n".join(lines)


def roadmap(skills):
    return "\n".join(f"- [{'x' if s['done'] else ' '}] {s['name']}" for s in skills)


def replace_block(text, tag, content):
    pattern = rf"(<!--START_{tag}-->)(.*?)(<!--END_{tag}-->)"
    return re.sub(pattern, lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text, flags=re.S)


data = json.loads(DATA.read_text(encoding="utf-8"))
text = README.read_text(encoding="utf-8")
text = replace_block(text, "PROJECTS", projects_table(data["projects"]))
text = replace_block(text, "ROADMAP", roadmap(data["skills"]))
README.write_text(text, encoding="utf-8")
print("README updated")
