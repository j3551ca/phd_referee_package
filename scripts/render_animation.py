"""Generate a consistent split-flap board with simultaneous, independently settling letters."""
from pathlib import Path
import re, math, random, textwrap
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
ROOT=Path(__file__).resolve().parents[1]
info=(ROOT/'Program_Info.md').read_text()
rows=[]
for line in info.splitlines():
    if line.startswith('| '):
        cells=[c.strip() for c in line.strip('|').split('|')]
        if len(cells)==7 and cells[0] not in ('University','---'):rows.append(cells)

def font(size):
    for name in ['DejaVuSansMono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/System/Library/Fonts/Menlo.ttc']:
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    raise RuntimeError('A monospace font is required')
FONT=font(27)
CW,CH,GAP=20,42,2
STEP=CW+GAP
COLS=[('university',40,12),('program',330,25),('deadline',910,23),('status',1440,12),('links',1730,12)]
W=2030
TOP=270
ROW=112
H=TOP+len(rows)*ROW+104
base=Image.new('RGB',(W,H),'#111921');d=ImageDraw.Draw(base)
def label(x,y,t,size=20,color='#c1ced8'):
    d.text((x,y),t,font=font(size),fill=color)
label(40,30,'DEPARTURES → DOCTORAL RESEARCH',30,'#f0c66a')
label(40,86,'JESSICA M. CALETA',38,'#ffffff')
label(40,148,'AUTUMN 2027  /  PROGRAMS, DEADLINES & REFERENCE GUIDANCE',22)
pending=sum(r[1]=='TBD' for r in rows)
label(40,193,f'{len(rows)} UNIVERSITIES   /   {len(rows)-pending} SELECTED   /   {pending} TO BE CONFIRMED',18)
for (kind,x,n),name in zip(COLS,['UNIVERSITY','PROGRAM','DEADLINE / PT/CT','APPLICATION','REFERENCE LINKS']):label(x,239,name,19,'#f0c66a')

@lru_cache(maxsize=128)
def card(ch):
    im=Image.new('RGB',(CW,CH),'#111921');q=ImageDraw.Draw(im)
    q.rounded_rectangle((0,0,CW-1,CH-1),radius=2,fill='#293946',outline='#3d4c58')
    q.text((CW/2,CH/2),ch,font=FONT,anchor='mm',fill='#f5edda')
    q.line((0,CH//2,CW,CH//2),fill='#111921',width=1)
    return im

def plain(s):return re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',s).replace('**','')
def lines_for(value,width):
    result=[]
    for line in value.split('\n'):
        result.extend(textwrap.wrap(line,width=width,break_long_words=False,break_on_hyphens=False) or [''])
    assert len(result)<=2,f'Value exceeds cell height: {value}'
    assert all(len(v)<=width for v in result),value
    return result

groups={}
for i,(uni,program,deadline,guidance,notes,status,links) in enumerate(rows):
    y=TOP+i*ROW
    d.rounded_rectangle((24,y,W-24,y+ROW-10),radius=5,fill='#1b2732')
    prog=plain(program).replace('PhD','').replace('DPhil in ','').strip(' —')
    if program=='TBD':prog='TO BE CONFIRMED'
    if '<br>' in deadline:
        date,times=deadline.split('<br>',1)
        # 24-hour PT/CT pair keeps both local times on one line without dropping seconds.
        def clock(t):
            match=re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a|p)\.m\.',t,re.I)
            if not match:
                match=re.search(r'(\d{1,2})\s*(a|p)\.m\.',t,re.I)
                hour=int(match[1])%12+(12 if match[2].lower()=='p' else 0)
                return f'{hour:02d}:00'
            hour=int(match[1])%12+(12 if match[4].lower()=='p' else 0)
            return f'{hour:02d}:{match[2]}'+(':'+match[3] if match[3] else '')
        pt,ct=times.split(' / ')
        dl=date+'\n'+clock(pt)+' / '+clock(ct)+('*' if '*' in times else '')
    else:dl='TO BE CONFIRMED' if deadline.startswith('TBD') else deadline.split(' — ')[0]+'\nTIME UNCONFIRMED'
    # Put a dated status on its second line, keeping invitation updates readable.
    compact_status=lambda value: re.sub(r'\s*\(([^)]+)\)',r'\n\1',value)
    vals=[uni,prog,dl,'NOT RECORDED' if status in ('—','') else compact_status(status),compact_status(links)]
    for line_no in range(2):
        # The row ruling and every character hinge occupy the exact same y coordinate.
        hinge=y+9+line_no*46+CH//2
        d.line((24,hinge,W-24,hinge),fill='#111921',width=1)
    for (kind,x,width),val in zip(COLS,vals):
        content=lines_for(plain(val).upper(),width)
        slots=[]
        for line_no in range(2):
            line=content[line_no] if line_no<len(content) else ''
            for j,ch in enumerate(line.ljust(width)):
                pos=(x+j*STEP,y+9+line_no*46)
                base.paste(card(ch),pos)
                if ch!=' ':slots.append((pos,ch))
        groups[(i,kind)]=slots
label(40,H-82,'TIMES: 24-HOUR PT/CT  ·  PT = B.C. (UTC-7)  ·  CT = SASKATCHEWAN (UTC-6)',18)
label(40,H-48,'* BERKELEY CUTOFF NEEDS CONFIRMATION. SEE THE FULL GUIDANCE TABLE BELOW.',18)
base.save(ROOT/'assets/application-board-still.png')
palette=base.quantize(colors=128)
def quant(im):return im.quantize(palette=palette,dither=Image.Dither.NONE)

@lru_cache(maxsize=8192)
def flap(old,new,phase):
    p=phase/5
    a,b=card(old),card(new);mid=CH//2
    result=a.copy();result.paste(b.crop((0,0,CW,mid)),(0,0))
    if p<0.5:
        h=max(1,round(mid*math.cos(p*math.pi)))
        moving=a.crop((0,0,CW,mid)).resize((CW,h),Image.Resampling.LANCZOS)
        moving=ImageEnhance.Brightness(moving).enhance(1-0.4*p*2)
        result.paste(moving,(0,mid-h))
    else:
        h=max(1,round((CH-mid)*math.sin((p-0.5)*math.pi)))
        moving=b.crop((0,mid,CW,CH)).resize((CW,h),Image.Resampling.LANCZOS)
        moving=ImageEnhance.Brightness(moving).enhance(0.6+0.4*(p-0.5)*2)
        result.paste(moving,(0,mid))
    ImageDraw.Draw(result).line((0,mid,CW,mid),fill='#111921')
    return result

rng=random.Random(27)
# No left-to-right offsets: all letters in each value start together.
# Up to four dispersed values animate per round; deadlines remain reliably visible.
rounds=[[(0,'university'),(3,'program'),(7,'status')],
        [(2,'program'),(5,'links'),(9,'university'),(1,'status')],
        [(6,'university'),(8,'program')],
        [(4,'program'),(10,'links'),(1,'university'),(6,'status')]]
frames=[quant(base)];durations=[3000]
alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
for selected in rounds:
    assert len(selected)<=4
    specs=[]
    for key in selected:
        for pos,ch in groups.get(key,[]):
            turns=rng.randint(3,6)
            # Individual letters settle after different numbers of rotations, independently of position.
            chars=[ch]+[rng.choice(alphabet) for _ in range(turns-1)]+[ch]
            specs.append((pos,chars))
    for n in range(6*6):
        im=base.copy();turn=n//6;phase=n%6
        for pos,chars in specs:
            if turn<len(chars)-1:im.paste(flap(chars[turn],chars[turn+1],phase),pos)
        frames.append(quant(im));durations.append(55)
    frames.append(quant(base));durations.append(5000)
path=ROOT/'assets/application-board.gif'
frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=1,optimize=True)
# Verify that dates and times never move, and the sequence returns to the actual data.
with Image.open(path) as gif:
    first=gif.convert('RGB');region=(900,TOP,1430,TOP+len(rows)*ROW)
    for i in range(gif.n_frames):
        gif.seek(i)
        assert ImageChops.difference(first.crop(region),gif.convert('RGB').crop(region)).getbbox() is None
    assert ImageChops.difference(first,gif.convert('RGB')).getbbox() is None
print(f'{len(frames)} frames; {sum(durations)/1000:.1f}s cycle; {path.stat().st_size:,} bytes; max 4 values; deadlines static.')
