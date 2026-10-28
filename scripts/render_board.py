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
board_line=next(line for line in readme.splitlines() if 'assets/application-board.gif' in line)
board_at=readme.index(board_line)
prefix=readme[:board_at]
# Replace existing sign groups, independently of whether a title exists.
prefix=re.sub(r'<p\b[^>]*>.*?</p>', lambda m: '' if re.search(r'assets/(?:academic-cv|research-brief|program-guide)-sign\.png',m[0]) else m[0], prefix, flags=re.S)
# Also handle signs flattened into one Markdown image line by visual editors.
prefix='\n'.join(line for line in prefix.splitlines() if not re.search(r'assets/(?:academic-cv|research-brief|program-guide)-sign\.png',line)).rstrip()
readme=(prefix+'\n\n' if prefix else '')+nav+'\n'+readme[board_at:]
# Keep the board link working even if a visual editor flattens its Markdown wrapper.
linked_board='[![Click the flight board to open Program Info: program links, deadlines, and recommendation-letter guidance](assets/application-board.gif)](Program_Info.md)'
readme=readme.replace(board_line,linked_board,1)
readme_path.write_text(readme,encoding='utf-8')
print(f'Restored navigation to Program Info; {len(rows)} programs remain in the source guide.')
