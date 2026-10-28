"""One non-looping header flip. No informational pixels move."""
from pathlib import Path
from io import BytesIO
import sys
from PIL import Image, ImageDraw, ImageChops
ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) > 1:
    base = Image.open(sys.argv[1]).convert('RGB')
else:
    import cairosvg
    base = Image.open(BytesIO(cairosvg.svg2png(url=str(ROOT/'assets/application-board.svg')))).convert('RGB')
# Only the 64 x 56 decorative arrow area is animated.
box = (24, 24, 88, 80)
tile = base.crop(box)
frames=[base.copy()]
for scale in [0.92,0.70,0.40,0.12,0.03,0.12,0.40,0.70,0.92]:
    frame=base.copy()
    ImageDraw.Draw(frame).rectangle((24,24,87,79),fill='#111921')
    height=max(1,round(tile.height*scale))
    flap=tile.resize((tile.width,height),Image.Resampling.LANCZOS)
    frame.paste(flap,(24,52-height//2))
    frames.append(frame)
frames.append(base.copy())
# Shared palette prevents color flicker outside the animated area.
palette=base.quantize(colors=256)
frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
path=ROOT/'assets/application-board.gif'
# Deliberately omit the loop extension: play once, then retain final frame.
frames[0].save(path,save_all=True,append_images=frames[1:],duration=[1200]+[90]*9+[1000],disposal=1,optimize=True)
with Image.open(path) as gif:
    assert 'loop' not in gif.info
    first=gif.convert('RGB')
    for i in range(gif.n_frames):
        gif.seek(i)
        changed=ImageChops.difference(first,gif.convert('RGB')).getbbox()
        assert changed is None or (changed[0]>=box[0] and changed[1]>=box[1] and changed[2]<=box[2] and changed[3]<=box[3]),changed
    assert ImageChops.difference(first,gif.convert('RGB')).getbbox() is None
print(f'Created {path.name}: {path.stat().st_size:,} bytes; one 810 ms flip; information unchanged.')
