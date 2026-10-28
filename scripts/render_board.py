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
W, H = 1710, 264 + len(rows)*76 + 94
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
'<title id="title">Jessica Caleta — PhD application departures board</title>',
'<desc id="desc">Application status and deadlines for eleven universities. The full accessible table and official reference guidance appear beneath this board.</desc>',
'<rect width="1710" height="'+str(H)+'" rx="20" fill="#111921"/>',
'<path d="M32 52h44m-22-13 22 13-22 13" fill="none" stroke="#f0c66a" stroke-width="4"/>']
def text(x,y,t,size=18,color='#e7edf1',weight='400',spacing=0):
    parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" fill="{color}">{escape(t)}</text>')
text(95,60,'NEXT DESTINATION: DOCTORAL RESEARCH',24,'#f0c66a','600',2)
text(36,115,'Jessica M. Caleta',36,'#ffffff','600')
text(36,151,'AUTUMN 2027  /  PROGRAMS, DEADLINES & REFERENCE GUIDANCE',16,'#a8b8c5','400',1.4)
pending = sum(r[1] == 'TBD' for r in rows)
text(36,191,f'{len(rows)} universities  ·  {len(rows)-pending} selected programs  ·  {pending} to be confirmed',17,'#a8b8c5')
text(1360,191,'UPDATED '+updated.upper(),13,'#a8b8c5')
for x,label in [(38,'DESTINATION'),(265,'PROGRAM'),(765,'DEADLINE · PT / CT'),(1180,'APPLICATION STATUS'),(1430,'REFERENCE LINKS')]:
    text(x,238,label,13,'#f0c66a','600',1.4)
for i,(uni,program,deadline,guidance,notes,status,invitations) in enumerate(rows):
    y=264+i*76
    parts.append(f'<rect x="24" y="{y}" width="1662" height="66" rx="5" fill="{("#1b2732" if i%2==0 else "#18232d")}"/>')
    # Split-flap-inspired fine center rule; text stays above and below for readability.
    parts.append(f'<path d="M25 {y+33}H1685" stroke="#111921" stroke-width="1" opacity="0.6"/>')
    text(38,y+27,uni.upper(),20,'#ffffff','600',0.7)
    display = 'Program to be confirmed' if program == 'TBD' else program.split('<br>')[0].replace('DPhil in ', '').replace('PhD', '').strip(' —')
    import textwrap
    wrapped = textwrap.wrap(display, width=43)
    for j, line in enumerate(wrapped[:2]):
        text(265,y+27+j*26,line,18)
    ds=deadline.replace('**','').split('<br>')
    if len(ds)>1:
        text(765,y+25,ds[0].upper(),17,'#ffffff','600')
        text(765,y+53,ds[1],15,'#bdcbd5')
    elif deadline.startswith('TBD'):
        text(765,y+27,'TO BE CONFIRMED',16,'#bdcbd5')
    else:
        date=deadline.split(' — ')[0]
        text(765,y+25,date.upper(),17,'#ffffff','600')
        text(765,y+53,'Cutoff time to be confirmed',15,'#bdcbd5')
    shown='Not recorded' if status in ('—','') else status
    lower=shown.lower()
    color='#78d4b5' if lower.startswith('submitted') else '#f0c66a' if ('progress' in lower or 'started' in lower and not lower.startswith('not')) else '#a8b8c5'
    text(1180,y+27,shown[:24].upper(),15,color,'600')
    if len(shown)>24:text(1180,y+53,shown[24:],13,color)
    import textwrap
    for j, line in enumerate(textwrap.wrap(invitations.upper(), width=26)[:2]):
        text(1430,y+27+j*26,line,14,'#78d4b5' if invitations.lower().startswith('sent to all') else '#a8b8c5','600')
footer=264+len(rows)*76
text(36,footer+31,'PT = B.C./Vancouver (UTC−7)   ·   CT = Saskatchewan (UTC−6)',15,'#a8b8c5')
text(36,footer+59,'* Berkeley cutoff needs confirmation. Read deadline exceptions and official guidance in the table below.',15,'#a8b8c5')
parts.append('</svg>')
(ROOT/'assets/application-board.svg').write_text('\n'.join(parts))
readme='''# Jessica M. Caleta · PhD referee package

[Academic CV · PDF](Jessica_Caleta_Academic_CV.pdf) &nbsp; / &nbsp; [Research brief](Research_Brief.md) &nbsp; / &nbsp; [Program information](Program_Info.md)

![PhD application board with universities, deadlines and current application statuses](assets/application-board.gif)

[View the still board](assets/application-board.svg) · The decorative header flips once. All program information stays still.

Welcome, and thank you for supporting my autumn 2027 PhD applications. This page is the central reference for my program choices, deadlines, and application progress. The table below includes the official instructions for referees. Application status does not indicate whether a reference letter has been submitted.

'''
readme += info.replace('# PhD Programs, Deadlines & Reference Letter Guide','## Programs, deadlines & reference letters',1)
readme += '''

<details>
<summary>Updating the board</summary>

Edit the **Application status** and **Reference links sent** columns in [Program_Info.md](Program_Info.md), then commit the change to `main`. Use “In progress”, “Submitted (date)”, or “Withdrawn”, as appropriate. Keep an unrecorded status as “—”. You can also update program choices, deadlines, and notes in the same file, including the date at the top.

GitHub Actions refreshes this landing page and its board after each edit. To regenerate locally, run `python3 scripts/render_board.py` followed by `python3 scripts/render_animation.py` (requires Pillow and CairoSVG). The full table preserves the exact status wording and all guidance links.

</details>
'''
(ROOT/'README.md').write_text(readme)
print(f'Rendered {len(rows)} programs from Program_Info.md')
