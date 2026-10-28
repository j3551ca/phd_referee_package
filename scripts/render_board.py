"""Render the landing page from Program_Info.md using only Python's standard library."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
info = (ROOT / 'Program_Info.md').read_text()
rows = []
for line in info.splitlines():
    if not line.startswith('| '):
        continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    if len(cells) != 7 or cells[0] in ('University', '---'):
        continue
    rows.append(cells)
assert len(rows) > 0, 'No program rows found'
updated = re.search(r'Updated ([^\n]+)', info)
updated = updated.group(1) if updated else 'See program guide'
readme='''# Jessica M. Caleta · PhD referee package

[Academic CV · PDF](Jessica_Caleta_Academic_CV.pdf) &nbsp; / &nbsp; [Research brief](Research_Brief.md) &nbsp; / &nbsp; [Program information](Program_Info.md)

![PhD application board with universities, deadlines and current application statuses](assets/application-board.gif)

[View the still board](assets/application-board-still.png) · Up to four values flip at once, with five-second pauses. Letters start together and settle independently. Deadlines stay still; the full table below is always readable.

Welcome, and thank you for supporting my autumn 2027 PhD applications. This page is the central reference for my program choices, deadlines, and application progress. The table below includes the official instructions for referees. Application status does not indicate whether a reference letter has been submitted.

'''
readme += info.replace('# PhD Programs, Deadlines & Reference Letter Guide','## Programs, deadlines & reference letters',1)
readme += '''

<details>
<summary>Updating the board</summary>

Edit the **Application status** and **Reference links sent** columns in [Program_Info.md](Program_Info.md), then commit the change to `main`. Use “In progress”, “Submitted (date)”, or “Withdrawn”, as appropriate. Keep an unrecorded status as “—”. You can also update program choices, deadlines, and notes in the same file, including the date at the top.

GitHub Actions refreshes this landing page and its board after each edit. To regenerate locally, run `python3 scripts/render_board.py` followed by `python3 scripts/render_animation.py` (requires Pillow). The full table preserves the exact status wording and all guidance links.

</details>
'''
(ROOT/'README.md').write_text(readme)
print(f'Rendered {len(rows)} programs from Program_Info.md')
