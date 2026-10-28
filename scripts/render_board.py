"""Refresh navigation and the program table while preserving other README edits."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
info=(ROOT/'Program_Info.md').read_text(encoding='utf-8')
readme_path=ROOT/'README.md'
readme=readme_path.read_text(encoding='utf-8')
rows=[]
for line in info.splitlines():
    if not line.startswith('| '):continue
    cells=[cell.strip() for cell in line.strip('|').split('|')]
    if len(cells)==7 and cells[0] not in ('University','---'):rows.append(cells)
assert rows, "No program rows found"
nav='''<p align="center">
<a href="Jessica_Caleta_Academic_CV.pdf"><img src="assets/academic-cv-sign.png" alt="Academic CV — qualifications and publications" width="32%"></a>
<a href="Research_Brief.md"><img src="assets/research-brief-sign.png" alt="Research brief — interests and experience" width="32%"></a>
<a href="Program_Info.md"><img src="assets/program-guide-sign.png" alt="Program guide — deadlines and references" width="32%"></a>
</p>
'''
# A visual Markdown editor can flatten the linked HTML signs. Restore their source markup.
first_break=readme.index('\n\n')
board_line=next(line for line in readme.splitlines() if 'assets/application-board.gif' in line)
board_at=readme.index(board_line)
readme=readme[:first_break+2]+nav+'\n'+readme[board_at:]
lines=readme.splitlines()
start=next(i for i,line in enumerate(lines) if line.startswith('| University'))
end=start
while end<len(lines) and lines[end].startswith('|'):end+=1
table=['| University | Program | Deadline | Recommendation letter guidelines | Application status | Recommendation letter link | Notes |',
       '| --- | --- | --- | --- | --- | --- | --- |']
for university,program,deadline,guidance,status,link_status,note in rows:
    note='' if note in ('—','') else note
    table.append('| '+' | '.join([f'**{university}**',program,deadline,guidance,status,link_status,note])+' |')
lines[start:end]=table
readme_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Restored three linked signs and refreshed {len(rows)} program rows; other README text preserved.')
