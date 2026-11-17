# GPT가 그린 7칸 만화 한 장을 칸별로 자르기: python3 comic_slice.py 그림파일
import sys, os, numpy as np
from PIL import Image
src = sys.argv[1]; out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comic_gpt"); os.makedirs(out, exist_ok=True)
im = Image.open(src).convert("RGB"); a = np.asarray(im.convert("L")).astype(int); H, W = a.shape
def runs(mask):   # True가 이어진 구간들
    r, s = [], None
    for i, v in enumerate(mask):
        if v and s is None: s = i
        if not v and s is not None: r.append((s, i)); s = None
    if s is not None: r.append((s, len(mask)))
    return r
def bands(prof, n, minlen):
    # prof: 줄마다 '거의 흰색' 비율 → 흰 여백이 아닌 구간(칸)을 길이순 n개
    content = runs(prof < 0.99)
    content = [c for c in content if c[1] - c[0] >= minlen]
    return content
rowp = (a > 245).mean(axis=1)
rows = bands(rowp, 4, H // 12)
if len(rows) != 4: sys.exit(f"가로줄을 4개로 못 나눔: {rows}")
k = 1
for ri, (y0, y1) in enumerate(rows):
    if ri < 3:
        colp = (a[y0:y1] > 232).mean(axis=0)
        cols = bands(colp, 2, W // 6)
        if len(cols) != 2: sys.exit(f"{ri+1}번째 줄을 2칸으로 못 나눔: {cols}")
    else:
        cols = [(0, W)]
        colp = (a[y0:y1] > 232).mean(axis=0); c2 = bands(colp, 1, W // 3); cols = c2[:1] or cols
    for (x0, x1) in cols:
        im.crop((x0, y0, x1, y1)).save(os.path.join(out, f"comic_{k}.png")); k += 1
print("잘라 낸 칸:", k - 1, "→", out)
