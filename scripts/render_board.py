"""Keep README navigation linked to the full guide; the table lives only in Program_Info.md."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
info=(ROOT/'Program_Info.md').read_text(encoding='utf-8')
readme_path=ROOT/'README.md'
readme=readme_path.read_text(encoding='utf-8')
rows=[]
for line in info.splitlines():
    if not line.startswith('| '):continue
    cells=[cell.strip() for cell in line.strip('|').split('|')]
    if len(cells)==7 and cells[0] != 'University' and not all(re.fullmatch(r':?-+:?', c) for c in cells):rows.append(cells)
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
# Keep the board link working even if a visual editor flattens its Markdown wrapper.
linked_board='[![Click the flight board to open Program Info: program links, deadlines, and recommendation-letter guidance](assets/application-board.gif)](Program_Info.md)'
readme=readme.replace(board_line,linked_board,1)
readme_path.write_text(readme,encoding='utf-8')
print(f'Restored navigation to Program Info; {len(rows)} programs remain in the source guide.')
