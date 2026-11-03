#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
readme = root / "README.md"
checklist_dir = root / "checklista"

# wczytaj README.md
content = readme.read_text(encoding="utf-8")

marker = "<!-- AUTO-CHECKLIST -->"
if marker not in content:
    print("❌ Auto-generated section not found in README.md", file=sys.stderr)
    sys.exit(1)

# --- usuń wszystko przed pierwszym nagłówkiem '#'
lines = content.splitlines()
for idx, line in enumerate(lines):
    if line.strip().startswith("#"):
        first_header_idx = idx
        break
else:
    first_header_idx = 0

lines = lines[first_header_idx:]
content = "\n".join(lines)

# --- uruchomienie gen_json.py (w katalogu checklist)
subprocess.run(["python3", "gen_json.py"], cwd=checklist_dir, check=True)

# --- generowanie SVG po gen_json.py
subprocess.run(["python3", "gen_svg.py"], cwd=checklist_dir, check=True)

# --- dodaj obrazek oi_progress.svg nad pierwszym nagłówkiem
svg_path = "checklista/oi_progress.svg"
if lines:
    content = f"![Progres OI]({svg_path})\n\n" + content
else:
    content = f"![Progres OI]({svg_path})\n"

tables = []

# uruchomienie gen_liczniki.py
out = subprocess.check_output(
    ["python3", "gen_liczniki.py"],
    cwd=checklist_dir,
    text=True
)
tables.append("\n\n" + out.strip() + "\n")

roman = {1: "I", 2: "II", 3: "III"}

# uruchomienie 3 generatorów (również w katalogu checklist)
for etap in [1, 2, 3]:
    out = subprocess.check_output(
        ["python3", f"gen_etap{etap}_checklist.py"],
        cwd=checklist_dir,
        text=True
    )
    tables.append(f"## Solved tasks from Stage {roman[etap]}\n\n" + out.strip() + "\n")

# komunikat ostrzegawczy
warning = (
    "> ⚠️ **NOTE:** The section below is generated automatically.\n"
    "> Do not modify the README below this notice.\n"
    "> ✅ means a completed task.\n"
    "> 🤔 means a task with fewer than 100 points.\n"
)

# podmiana zawartości po markerze
if marker in content:
    base, _ = content.split(marker, 1)
else:
    base = content

new_content = base + marker + "\n\n" + warning + "\n\n".join(tables)

# zapisz
readme.write_text(new_content, encoding="utf-8")
print("✅ README.md has been updated")

