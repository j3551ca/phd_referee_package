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

<table>
<tr>
<td align="center"><a href="Jessica_Caleta_Academic_CV.pdf"><img src="assets/academic-cv-sign.svg" alt="Academic CV — qualifications and publications" width="200"></a></td>
<td align="center"><a href="Research_Brief.md"><img src="assets/research-brief-sign.svg" alt="Research brief — interests and experience" width="200"></a></td>
<td align="center"><a href="Program_Info.md"><img src="assets/program-guide-sign.svg" alt="Program guide — deadlines and references" width="200"></a></td>
</tr>
</table>

[![PhD application board — click to jump to linked programs and guidance](assets/application-board.gif)](#programs-deadlines--reference-letters)

[View the still board](assets/application-board-still.png) · Up to four values flip at once, with five-second pauses. Letters start together and settle independently. Deadlines stay still; the full table below is always readable.

Welcome, and thank you for supporting my autumn 2027 PhD applications. This page is the central reference for my program choices, deadlines, and application progress. The table below includes the official instructions for referees. Application status does not indicate whether a reference letter has been submitted.

'''
# Keep the editable seven-column source, but present a compact four-column view.
start=info.index('| University |')
lines=info[start:].splitlines()
last=0
for i,line in enumerate(lines):
    if line.startswith('| '): last=i
suffix='\n'.join(lines[last+1:])
intro=info[:start].replace('# PhD Programs, Deadlines & Reference Letter Guide','## Programs, deadlines & reference letters',1)
readme += intro
readme += '| University / program | Deadline | Progress | Referee guidance |\n| --- | --- | --- | --- |\n'
notes=[]
for uni,program,deadline,guidance,note,status,invitations in rows:
    links=re.findall(r'\[([^]]+)\]\(([^)]+)\)',guidance)
    primary='[Instructions]('+links[0][1]+')' if links else guidance
    anchor=re.sub(r'[^a-z0-9]+','-',uni.lower()).strip('-')+'-notes'
    if note not in ('—','') or len(links)>1:
        primary += '<br>[Notes & sources](#'+anchor+')'
        extra=' · '.join('['+label+']('+url+')' for label,url in links[1:])
        notes.append('### '+uni+' notes\n\n'+(note+'\n\n' if note not in ('—','') else '')+extra+'\n')
    shown='Not recorded' if status in ('—','') else status
    deadline=deadline.replace(' / ','<br>')
    progress='**Application:** '+shown+'<br>**Links:** '+invitations
    readme += '| **'+uni+'**<br>'+program+' | '+deadline+' | '+progress+' | '+primary+' |\n'
readme += '\n'+suffix+'\n\n## Reference notes & sources\n\n'+'\n'.join(notes)

readme += '''

<details>
<summary>Updating the board</summary>

Edit the **Application status** and **Reference links sent** columns in [Program_Info.md](Program_Info.md), then commit the change to `main`. Use “In progress”, “Submitted (date)”, or “Withdrawn”, as appropriate. Keep an unrecorded status as “—”. You can also update program choices, deadlines, and notes in the same file, including the date at the top.

GitHub Actions refreshes this landing page and its board after each edit. To regenerate locally, run `python3 scripts/render_board.py` followed by `python3 scripts/render_animation.py` (requires Pillow). The full table preserves the exact status wording and all guidance links.

</details>
'''
(ROOT/'README.md').write_text(readme)
print(f'Rendered {len(rows)} programs from Program_Info.md')
