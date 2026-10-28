"""Render the landing page from Program_Info.md using only Python's standard library."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
info = (ROOT / "Program_Info.md").read_text(encoding="utf-8")

rows = []
for line in info.splitlines():
    if not line.startswith("| "):
        continue
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if len(cells) != 7 or cells[0] in ("University", "---"):
        continue
    rows.append(cells)

assert rows, "No program rows found"

readme = """# Jessica M. Caleta · PhD referee package

![Academic CV — qualifications and publications](assets/academic-cv-sign.png) ![Research brief — interests and experience](assets/research-brief-sign.png) ![Program guide — deadlines and references](assets/program-guide-sign.png)

![PhD application board — click to jump to linked programs and guidance](assets/application-board.gif)

Welcome, and thank you for supporting my autumn 2027 PhD applications. This page is the central reference for my program choices, deadlines, and application progress. The table below links to the best official recommendation-letter guidance available; applicant-facing pages are labeled. Application status does not indicate whether a recommendation letter has been submitted.

"""

table_start = info.index("| University |")
table_lines = info[table_start:].splitlines()
last_table_line = max(
    index for index, line in enumerate(table_lines) if line.startswith("| ")
)
suffix = "\n".join(table_lines[last_table_line + 1 :])
intro = info[:table_start].replace(
    "# PhD Programs, Deadlines & Recommendation Letter Guide",
    "## Programs, deadlines & recommendation letters",
    1,
)
# Keep the landing page concise; the full source guide retains the deadline note.
intro = re.sub(r"\*\*Deadline:\*\*.*?\n\n", "", intro)
intro = intro.replace("These labels reflect the referees’ locations. ", "")
readme += intro

readme += (
    "| University | Program | Deadline | Recommendation letter guidelines | "
    "Application status | Reference link status | Notes |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
)

for university, program, deadline, guidance, status, link_status, note in rows:
    note = "" if note in ("—", "") else note
    readme += (
        f"| **{university}** | {program} | {deadline.replace(' / ', '<br>')} | "
        f"{guidance} | {status} | {link_status} | {note} |\n"
    )

readme += f"\n{suffix}\n"
readme += """

Updating the board

Edit the **Application status** and **Reference link status** columns in [Program_Info.md](Program_Info.md), then commit the change to `main`. For reference links, use only “Sent”, “Not sent”, or “Not recorded”. You can also update program choices, deadlines, and notes in the same file, including the date at the top.

GitHub Actions refreshes this landing page and its board after each edit. To regenerate locally, run `uv run python scripts/render_board.py` followed by `uv run --with pillow python scripts/render_animation.py`. The full table preserves the exact status wording and all guidance links.
"""

(ROOT / "README.md").write_text(readme, encoding="utf-8")
print(f"Rendered {len(rows)} programs from Program_Info.md")
