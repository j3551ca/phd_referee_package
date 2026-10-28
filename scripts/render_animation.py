"""Quiet split-flap board: dispersed card flips, long pauses, static deadlines."""
from pathlib import Path
from io import BytesIO
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)>1:
    base=Image.open(sys.argv[1]).convert('RGB')
else:
    import cairosvg
    base=Image.open(BytesIO(cairosvg.svg2png(url=str(ROOT/'assets/application-board.svg')))).convert('RGB')
font=None
for name in ['DejaVuSansMono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/System/Library/Fonts/Menlo.ttc']:
    try: font=ImageFont.truetype(name,17);break
    except OSError: pass
if font is None: raise RuntimeError('A monospace font is required')
rows=[]
for line in (ROOT/'Program_Info.md').read_text().splitlines():
    if line.startswith('| '):
        row=[x.strip() for x in line.strip('|').split('|')]
        if len(row)==7 and row[0] not in ('University','---'):rows.append(row)
CW,CH,GAP=17,29,2

def card(char):
    im=Image.new('RGB',(CW,CH),'#18232d');d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,CW-1,CH-1),radius=2,fill='#273642',outline='#354552')
    d.text((CW/2,CH/2),char,font=font,anchor='mm',fill='#f2e8cd')
    d.line((0,CH//2,CW,CH//2),fill='#0b1117',width=1)
    return im

groups={}
for i,row in enumerate(rows):
    y=264+i*76
    for kind,x,val in [('university',38,row[0].upper()),('status',1180,'NOT RECORDED' if row[5] in ('—','') else row[5].upper()),('links',1430,row[6].upper())]:
        # Retain long detailed statuses as typeset text; never truncate them into misleading cards.
        if len(val)>12:continue
        ImageDraw.Draw(base).rectangle((x,y+3,x+(216 if kind == 'university' else 238),y+61),fill=('#1b2732' if i%2==0 else '#18232d'))
        slots=[]
        for j,ch in enumerate(val):
            pos=(x+j*(CW+GAP),y+9)
            base.paste(card(ch),pos);slots.append((pos,ch))
        groups[(i,kind)]=slots
palette=base.quantize(colors=256)
def quant(im):return im.quantize(palette=palette,dither=Image.Dither.NONE)
frames=[quant(base)];durations=[5000]
alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def intermediate(ch):
    return alphabet[(alphabet.index(ch)+9)%26] if ch in alphabet else ch

def flap(old,new,p):
    a,b=card(old),card(new);mid=CH//2
    result=a.copy();result.paste(b.crop((0,0,CW,mid)),(0,0))
    if p<0.5:
        h=max(1,round(mid*math.cos(p*math.pi)))
        moving=a.crop((0,0,CW,mid)).resize((CW,h),Image.Resampling.LANCZOS)
        moving=ImageEnhance.Brightness(moving).enhance(1-0.45*p*2)
        result.paste(moving,(0,mid-h))
    else:
        h=max(1,round((CH-mid)*math.sin((p-0.5)*math.pi)))
        moving=b.crop((0,mid,CW,CH)).resize((CW,h),Image.Resampling.LANCZOS)
        moving=ImageEnhance.Brightness(moving).enhance(0.55+0.45*(p-0.5)*2)
        result.paste(moving,(0,mid))
    ImageDraw.Draw(result).line((0,mid,CW,mid),fill='#080e13')
    return result

sequence=[(0,'university'),(2,'links'),(4,'status'),(6,'university'),(8,'status'),(10,'links')]
for key in sequence:
    slots=groups.get(key)
    if not slots:continue
    duration=0.70+0.045*(len(slots)-1)
    count=math.ceil(duration/0.07)+1
    for n in range(count):
        t=n*0.07;im=base.copy()
        for j,(pos,ch) in enumerate(slots):
            local=t-j*0.045
            if 0<=local<0.70:
                cycle=local/0.35
                old,new=(ch,intermediate(ch)) if cycle<1 else (intermediate(ch),ch)
                im.paste(flap(old,new,cycle%1),pos)
        frames.append(quant(im));durations.append(70)
    frames.append(quant(base));durations.append(10000)
path=ROOT/'assets/application-board.gif'
frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=1,optimize=True)
with Image.open(path) as gif:
    first=gif.convert('RGB')
    deadlines=first.crop((755,250,1160,1100))
    for i in range(gif.n_frames):
        gif.seek(i)
        assert ImageChops.difference(deadlines,gif.convert('RGB').crop((755,250,1160,1100))).getbbox() is None
    assert ImageChops.difference(first,gif.convert('RGB')).getbbox() is None
base.save(ROOT/'assets/application-board-still.png')
print(f'{len(frames)} frames, {sum(durations)/1000:.1f}s cycle, {path.stat().st_size:,} bytes. Deadline pixels unchanged.')
