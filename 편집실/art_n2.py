# Nova 제2호 도판 (art_v2.py와 같은 결: 잉크 선화 + 빨강/남색 + 망점, 종이 바탕)
# 실행: python3 편집실/art_n2.py  → 편집실/issues/2026-11-20/figs/<이름>.svg
# 그림 이름 = 원고 figs의 svg 값. 숫자는 원고 brief·facts 그대로이고, 축척은 아래 코드에서 계산해요.
import math, os, re, random

INK, RED, NAVY, PAPER, GRAY = "#1C1A17", "#C8372D", "#1F3A5F", "#FBF8F1", "#6B655C"
FAINT = "#8E9AAA"        # 회색빛 남색(옅은 선)
LIGHT = "#F4EFE4"        # 밤하늘 위 글자·점
ROCK = "#B9C0C8"
SANS = "'Noto Sans KR','Noto Sans CJK KR',sans-serif"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issues", "2026-11-20", "figs")

DEFS = f'''<defs>
<pattern id="dot" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="{INK}" opacity=".55"/></pattern>
<pattern id="dotR" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.3" fill="{RED}" opacity=".75"/></pattern>
<pattern id="dotRd" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.25" fill="{RED}" opacity=".9"/></pattern>
<pattern id="dotRs" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.2" fill="{RED}" opacity=".7"/></pattern>
<pattern id="dotN" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.2" fill="{NAVY}" opacity=".6"/></pattern>
<pattern id="dotP" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r=".9" fill="{PAPER}" opacity=".35"/></pattern>
<pattern id="dotF" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.1" fill="{FAINT}" opacity=".8"/></pattern>
<pattern id="dotG" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.2" fill="{NAVY}" opacity=".35"/></pattern>
<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="{INK}" stroke-width="1.2" opacity=".5"/></pattern>
<pattern id="hatchN" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="{NAVY}" stroke-width="1.1" opacity=".45"/></pattern>
<marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{INK}"/></marker>
<marker id="arrR" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{RED}"/></marker>
<marker id="arrN" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{NAVY}"/></marker>
<marker id="arrF" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{FAINT}"/></marker>
<marker id="arrP" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{LIGHT}"/></marker>
<marker id="tick" markerWidth="2" markerHeight="12" refX="1" refY="6" orient="auto"><rect width="2" height="12" fill="{INK}"/></marker>
</defs>'''


def svg(name, w, h, body, bg=PAPER):
    """한 파일 SVG. 여러 그림이 한 화면에 들어가도 id가 겹치지 않게 그림 이름을 앞에 붙여요."""
    p = name.replace("_", "-") + "-"
    s = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}" role="img">{DEFS}<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'
    s = re.sub(r'id="([A-Za-z]\w*)"', lambda m: f'id="{p}{m.group(1)}"', s)
    s = re.sub(r'url\(#([A-Za-z]\w*)\)', lambda m: f'url(#{p}{m.group(1)})', s)
    return s


def t(x, y, s, size=18, color=INK, anchor="start", weight=700, extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{extra}>{s}</text>'


def tl(x, y, lines, size=18, color=INK, anchor="start", weight=700, lh=1.3):
    return "".join(t(x, y + i * size * lh, s, size, color, anchor, weight) for i, s in enumerate(lines))


def tw(s, size):
    """글자 폭 어림(한글 1em, 숫자·영문 0.58em, 빈칸 0.3em)."""
    w = 0
    for ch in s:
        if ch == " ": w += 0.3
        elif ord(ch) < 0x1100 or ch in "·×→=+−:,.()%°~": w += 0.6
        else: w += 1.0
    return w * size


def tb(x, y, s, size=18, color=INK, anchor="start", weight=700, fill=PAPER, pad=6):
    w = tw(s, size) + pad * 2; h = size + pad + 4
    x0 = x - pad if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w + pad)
    return f'<rect x="{x0:.1f}" y="{y - size - 1:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{color}" stroke-width="1.2"/>' + t(x, y, s, size, color, anchor, weight)


def line(x1, y1, x2, y2, c=INK, w=1.5, dash="", mk=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{mk})"' if mk else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d}{m} stroke-linecap="round"/>'


def stars(x0, y0, w, h, n, seed=1, color=LIGHT, rmax=1.6):
    r = random.Random(seed); out = []
    for _ in range(n):
        out.append(f'<circle cx="{x0 + r.uniform(0, w):.1f}" cy="{y0 + r.uniform(0, h):.1f}" r="{r.choice([0.7, 1.0, rmax]):.1f}" fill="{color}" opacity="{r.choice([.5, .75, 1])}"/>')
    return "".join(out)


# ---------------------------------------------------------------- 고릴라(다 자란 암컷: 은빛 등 털·머리 볏 없음, 꼬리 없음)
# 네 발 자세(오른쪽을 봄). 바닥 y=0. 팔이 다리보다 길어 어깨(약 -158)가 엉덩이(약 -125)보다 높아요.
# 앞발은 주먹을 말아 손가락 마디로 짚고(흰 선 세 줄), 뒷발은 발바닥으로 디뎌요.
QUAD_BODY = ("M-112,-95 C-118,-120 -96,-129 -70,-126 C-32,-131 8,-150 44,-158 C64,-163 80,-157 90,-147 "
             "C97,-160 122,-160 129,-143 C133,-136 136,-129 133,-121 L138,-115 C141,-103 135,-93 124,-91 "
             "C115,-89 106,-92 100,-96 C95,-90 92,-84 88,-78 C92,-52 96,-28 97,-14 C106,-12 108,-1 99,1 "
             "L64,1 C59,-4 61,-10 66,-14 C60,-40 54,-62 44,-78 C30,-72 0,-68 -30,-71 C-45,-67 -51,-58 -49,-50 "
             "C-45,-37 -41,-25 -43,-14 C-40,-7 -28,-4 -20,1 L-67,1 C-73,-20 -81,-40 -98,-60 C-108,-72 -112,-85 -112,-95 Z")
QUAD_FAR = ("M30,-80 C42,-50 50,-28 52,-14 C60,-12 62,-1 54,1 L28,1 C24,-4 26,-10 30,-14 C26,-40 18,-62 12,-76 Z "
            "M-80,-70 C-74,-50 -70,-30 -72,-14 C-68,-7 -58,-4 -50,1 L-92,1 C-96,-22 -100,-44 -104,-62 Z")


def gorilla_quad(x, y, s=1.0, flip=False, fill=INK, far=None, detail=True, stroke=None, halo=None):
    sx = -s if flip else s
    far = far or fill
    st = stroke or fill
    d = ""
    if detail:
        d = (f'<path d="M72,-11 q8,-3 14,1 M74,-6 q8,-3 15,1 M78,-1 q6,-2 12,0" stroke="{PAPER}" stroke-width="1.4" fill="none" opacity=".8"/>'
             f'<path d="M44,-78 C56,-60 62,-40 66,-14" stroke="{PAPER}" stroke-width="1.2" fill="none" opacity=".45"/>'
             f'<path d="M-30,-71 C-36,-90 -60,-104 -86,-100" stroke="{PAPER}" stroke-width="1.2" fill="none" opacity=".45"/>'
             f'<path d="M-49,-50 C-60,-60 -74,-64 -88,-62" stroke="{PAPER}" stroke-width="1.1" fill="none" opacity=".35"/>'
             f'<circle cx="122" cy="-122" r="2.2" fill="{PAPER}" opacity=".9"/>'
             f'<path d="M116,-127 q8,-4 16,0" stroke="{PAPER}" stroke-width="1.3" fill="none" opacity=".7"/>'
             f'<path d="M133,-106 q-5,3 -10,2" stroke="{PAPER}" stroke-width="1.1" fill="none" opacity=".6"/>')
    h = f'<path d="{QUAD_BODY} {QUAD_FAR}" fill="{halo}" stroke="{halo}" stroke-width="{6 / s:.1f}" stroke-linejoin="round"/>' if halo else ""
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({sx:.3f},{s:.3f})">'
            f'{h}<path d="{QUAD_FAR}" fill="{far}" stroke="{st}" stroke-width="1"/>'
            f'<path d="{QUAD_BODY}" fill="{fill}" stroke="{st}" stroke-width="{1.5 / s:.2f}" stroke-linejoin="round"/>'
            f'<path d="{QUAD_BODY}" fill="url(#dotP)" opacity=".9"/>{d}</g>')


# 두 발로 선 자세(오른쪽을 봄). 발바닥 y=0. 다리는 짧고 굽었고, 팔이 길어요.
# arm="up": 한 팔을 위로 쭉 뻗고(손 끝 약 -262), 다른 팔은 뒤로 벌려 균형.
STAND_BODY = ("M-30,-66 C-42,-92 -42,-130 -30,-150 C-22,-162 -10,-168 -2,-170 "
              "C-2,-188 8,-206 26,-208 C42,-209 52,-198 52,-186 L57,-178 C60,-166 54,-156 44,-155 "
              "C40,-152 36,-150 32,-148 C44,-134 48,-116 46,-98 C48,-84 42,-72 32,-62 C24,-58 -20,-58 -30,-66 Z "
              "M-28,-66 C-36,-46 -38,-26 -32,-10 L-38,1 L-6,1 C-10,-8 -12,-30 -6,-52 Z "
              "M-8,-66 C-2,-46 2,-30 6,-14 C4,-6 6,0 10,1 L46,1 C44,-6 36,-10 28,-12 C30,-30 32,-48 30,-66 Z")
ARM_UP = "M-16,-156 C-12,-192 -6,-226 2,-250 C4,-260 16,-268 24,-262 C31,-256 28,-246 20,-240 C18,-214 16,-186 20,-150 Z"
ARM_BACK = "M-16,-154 C-44,-154 -74,-148 -98,-138 C-110,-135 -114,-122 -104,-117 C-97,-114 -92,-119 -90,-123 C-66,-128 -40,-128 -18,-124 Z"
ARM_DOWN = "M-10,-150 C-20,-120 -26,-90 -26,-60 C-32,-52 -30,-40 -20,-40 C-12,-40 -10,-50 -12,-58 C-8,-86 0,-116 8,-146 Z"
ARM_PUSH = "M14,-150 C40,-130 62,-104 76,-80 C82,-74 92,-74 92,-82 C92,-90 84,-92 80,-90 C66,-112 46,-136 30,-156 Z"


def gorilla_stand(x, y, s=1.0, flip=False, fill=INK, arm="up", detail=True, halo=None):
    sx = -s if flip else s
    arms = {"up": ARM_UP + " " + ARM_BACK, "down": ARM_DOWN, "push": ARM_PUSH, "upback": ARM_UP + " " + ARM_BACK}[arm]
    d = ""
    if detail:
        d = (f'<circle cx="44" cy="-185" r="2.2" fill="{PAPER}" opacity=".9"/>'
             f'<path d="M38,-191 q8,-4 16,0" stroke="{PAPER}" stroke-width="1.3" fill="none" opacity=".7"/>'
             f'<path d="M-20,-38 C-12,-46 6,-50 26,-46" stroke="{PAPER}" stroke-width="1.1" fill="none" opacity=".4"/>'
             f'<path d="M28,-22 C18,-24 8,-20 2,-12" stroke="{PAPER}" stroke-width="1.1" fill="none" opacity=".4"/>')
    hl = ""
    if halo:
        hl = f'<path d="{STAND_BODY} {arms}" fill="{halo}" stroke="{halo}" stroke-width="{5 / s:.1f}" stroke-linejoin="round"/>'
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({sx:.3f},{s:.3f})">{hl}'
            f'<path d="{arms}" fill="{fill}" stroke="{fill}" stroke-width="{1.5 / s:.2f}" stroke-linejoin="round"/>'
            f'<path d="{STAND_BODY}" fill="{fill}" stroke="{fill}" stroke-width="{1.5 / s:.2f}" stroke-linejoin="round"/>'
            f'<path d="{STAND_BODY} {arms}" fill="url(#dotP)" opacity=".9"/>{d}</g>')


def leaf(x, y, a, L=16, w=7, fill="url(#dotN)", stroke=INK):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({a:.0f})"><path d="M0,0 C{w},{-L * .3:.1f} {w},{-L * .8:.1f} 0,{-L} C{-w},{-L * .8:.1f} {-w},{-L * .3:.1f} 0,0 Z" '
            f'fill="{PAPER}" stroke="{stroke}" stroke-width="1.2"/><path d="M0,0 C{w},{-L * .3:.1f} {w},{-L * .8:.1f} 0,{-L} C{-w},{-L * .8:.1f} {-w},{-L * .3:.1f} 0,0 Z" fill="{fill}"/>'
            f'<line x1="0" y1="0" x2="0" y2="{-L * .9:.1f}" stroke="{stroke}" stroke-width=".8"/></g>')


def crown(cx, cy, rx, ry, n, seed):
    r = random.Random(seed); out = []
    blobs = []
    for i in range(n):
        a = r.uniform(0, 2 * math.pi); rr = math.sqrt(r.uniform(0, 1))
        blobs.append((cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr, r.uniform(26, 44)))
    blobs.sort(key=lambda b: b[1])
    for x, y, rad in blobs:
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad:.0f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>')
    for x, y, rad in blobs:
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad - 2:.0f}" fill="url(#dotN)" opacity=".75"/>')
    return "".join(out)


def bolt(x, y, s=1.0, c=RED):
    return f'<path transform="translate({x},{y}) scale({s})" d="M3,-12 L-5,1 L0,1 L-3,12 L6,-2 L1,-2 L4,-12 Z" fill="{c}" stroke="{INK}" stroke-width=".8"/>'


def fence(xs, ground, h, c=INK):
    out = []
    for x in xs:
        out.append(f'<rect x="{x - 3}" y="{ground - h}" width="6" height="{h}" fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
    for k, f in enumerate((0.25, 0.55, 0.85)):
        yy = ground - h * (1 - f)
        out.append(f'<polyline points="{" ".join(f"{x},{yy:.0f}" for x in xs)}" fill="none" stroke="{c}" stroke-width="1.4"/>')
    return "".join(out)


def rock(x0, x1, top, ground, seed=3, fill="url(#dotG)"):
    w = x1 - x0
    d = (f"M{x0},{ground} L{x0 + 6},{top + 14} Q{x0 + 10},{top + 2} {x0 + 30},{top} L{x1 - 34},{top - 1} "
         f"Q{x1 - 10},{top + 1} {x1 - 6},{top + 16} L{x1},{ground} Z")
    cracks = (f'<path d="M{x0 + w * .3:.0f},{top + 4} l8,16 l-6,12 M{x0 + w * .68:.0f},{top + 3} l-6,14 l9,14 M{x0 + w * .5:.0f},{ground - 4} l4,-14" '
              f'stroke="{INK}" stroke-width="1.2" fill="none" opacity=".6"/>')
    return f'<path d="{d}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><path d="{d}" fill="{fill}"/>{cracks}'


ART = {}

# ---------------------------------------------------------------- g2 대신: 고릴라 '살아 있는 사다리' 장면 (3:2, 높이 눈금 없음)
def scene_ladder(ox=0, oy=0, k=1.0, labels=True, sky=False):
    G = 484                       # 땅
    RT = 438                      # 바위 단 윗면(리샤 몸높이의 절반보다 낮게)
    LX, LS = 250, 0.86            # 리샤 자리·크기
    AX, AS = 238, 0.84            # 아멜리아 발 자리(리샤 등 위)·크기
    back_y = RT - 133 * LS        # 등 윗선(어깨와 허리 사이) 높이
    hand = (AX + 14 * AS, back_y - 258 * AS)
    b = []
    # 멀리 낮은 나무·구름
    b.append(f'<path d="M0,{G - 40} Q60,{G - 70} 120,{G - 44} Q170,{G - 80} 230,{G - 46} Q300,{G - 66} 360,{G - 42} L360,{G} L0,{G} Z" fill="url(#dotG)" opacity=".7"/>')
    b.append(f'<path d="M40,60 q14,-18 34,-8 q14,-16 32,-2 q20,0 18,14 z" fill="{PAPER}" stroke="{INK}" stroke-width="1.3" opacity=".8"/>')
    # 땅
    b.append(f'<rect x="0" y="{G}" width="720" height="{524 - G}" fill="url(#dotG)"/><line x1="0" y1="{G}" x2="720" y2="{G}" stroke="{INK}" stroke-width="2"/>')
    b.append("".join(f'<path d="M{x},{G} l3,-9 l3,9" stroke="{INK}" stroke-width="1" fill="none" opacity=".6"/>' for x in range(14, 720, 37)))
    # 나무(오른쪽): 줄기, 왼쪽 위로 뻗은 굵은 가지, 아래로 늘어진 잎가지
    tx = 610
    b.append(crown(650, 95, 100, 70, 15, 7))
    b.append(f'<path d="M{tx - 22},{G} C{tx - 16},{G - 120} {tx - 26},{G - 230} {tx - 12},{G - 330} L{tx + 22},{G - 330} C{tx + 16},{G - 220} {tx + 22},{G - 110} {tx + 30},{G} Z" fill="{PAPER}" stroke="{INK}" stroke-width="2.2"/>')
    b.append(f'<path d="M{tx - 22},{G} C{tx - 16},{G - 120} {tx - 26},{G - 230} {tx - 12},{G - 330} L{tx + 22},{G - 330} C{tx + 16},{G - 220} {tx + 22},{G - 110} {tx + 30},{G} Z" fill="url(#hatch)"/>')
    # 굵은 가지: 줄기 위쪽에서 왼쪽 위로 휘어 뻗음
    br = f"M{tx - 6},{G - 300} C{tx - 120},{G - 330} {hand[0] + 120},{18} {hand[0] - 70},{6} L{hand[0] - 72},{18} C{hand[0] + 110},{34} {tx - 120},{G - 310} {tx - 4},{G - 276} Z"
    b.append(f'<path d="{br}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><path d="{br}" fill="url(#hatch)" opacity=".6"/>')
    for (fx, fy, a) in [(hand[0] - 40, 12, -30), (hand[0] + 60, 26, 20), (hand[0] + 130, 50, -25), (hand[0] + 200, 78, 25), (hand[0] + 250, 100, -20), (hand[0] - 10, 22, 160), (hand[0] + 100, 44, 200), (hand[0] + 170, 70, 160)]:
        b.append(leaf(fx, fy, a, 16, 7))
    # 늘어진 가는 잎가지: 굵은 가지에서 아래로 늘어져 끝이 아멜리아 손에 닿음
    sx0, sy0 = hand[0] + 22, 22
    b.append(f'<path d="M{sx0},{sy0} C{sx0 + 4},{sy0 + 18} {hand[0] + 10},{hand[1] - 26} {hand[0] + 1},{hand[1] + 6}" stroke="{INK}" stroke-width="2.2" fill="none"/>')
    for (fx, fy, a) in [(sx0 + 2, sy0 + 12, 55), (sx0 + 3, sy0 + 22, -45), (hand[0] + 8, hand[1] - 22, 60), (hand[0] + 6, hand[1] - 14, -55), (hand[0] + 2, hand[1] + 6, 140), (hand[0] + 1, hand[1] + 8, -140)]:
        b.append(leaf(fx, fy, a, 14, 6))
    # 전기 울타리: 나무 밑동 둘레
    b.append(fence([tx - 70, tx - 20, tx + 50, tx + 96], G, 62))
    b.append(bolt(tx - 45, G - 46, 1.1))
    # 바위 단 + 리샤 + 아멜리아
    b.append(rock(LX - 120, LX + 150, RT, G))
    b.append(gorilla_quad(LX, RT, LS))
    b.append(gorilla_stand(AX, back_y + 1, AS, arm="up", halo=PAPER))
    if labels:
        b.append(line(132, 330, LX - 70, RT - 70, INK, 1.2))
        b.append(tb(40, 330, "리샤(받침)", 20))
        b.append(line(130, 180, AX - 40, back_y - 140, INK, 1.2))
        b.append(tb(30, 180, "아멜리아(손)", 20))
        b.append(tb(LX - 118, G + 31, "바위로 된 단", 20))
        b.append(line(tx - 110, G + 12, tx - 70, G - 30, INK, 1.2))
        b.append(tb(tx - 230, G + 31, "전기 울타리", 20, RED))
    return "".join(b)

ART["n2_gorilla_g2"] = svg("n2_gorilla_g2", 720, 524, scene_ladder())


# ---------------------------------------------------------------- 표지(4:5, 그림 속 글자 없음). 위쪽 3분의 1은 단순한 밤하늘
def cover():
    W, H = 800, 1000
    G = 772                     # 땅(아래쪽은 풀밭만: 화면이 머리기사 제목을 얹는 자리)
    RT = 728                    # 바위 단 윗면
    LX, LS, AX, AS = 330, 0.9, 319, 0.88
    back_y = RT - 133 * LS
    hand = (AX + 14 * AS, back_y - 258 * AS)
    b = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/><rect width="{W}" height="{H}" fill="url(#dot)" opacity=".3"/>']
    b.append(stars(0, 0, W, 330, 26, 11, LIGHT, 1.2))           # 위쪽: 작은 별 몇 개만
    b.append(stars(0, 330, W, 420, 40, 12, LIGHT, 1.6))
    # 지평선 쪽이 조금 밝은 초저녁 하늘(밝은 망점 띠)
    for i, (y0, op) in enumerate([(580, .10), (640, .18), (700, .28)]):
        b.append(f'<rect x="0" y="{y0}" width="{W}" height="{G - y0}" fill="url(#dotP)" opacity="{op * 2.4:.2f}"/>')
    # 크기가 아주 다른 별 둘: 큰 붉은 별(빨강 망점)과 바로 곁의 점 같은 작은 별(큰 별 지름의 20분의 1보다 작게)
    sx, sy, sr = 160, 455, 58
    b.append(f'<circle cx="{sx}" cy="{sy}" r="{sr + 26}" fill="none" stroke="{RED}" stroke-width="1.2" stroke-dasharray="2 6" opacity=".8"/>')
    b.append(f'<circle cx="{sx}" cy="{sy}" r="{sr + 12}" fill="none" stroke="{RED}" stroke-width="1.5" stroke-dasharray="3 5" opacity=".9"/>')
    b.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#EBB9A9" stroke="{RED}" stroke-width="2.5"/><circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#dotRd)"/>')
    b.append(f'<circle cx="{sx - 14}" cy="{sy - 16}" r="{sr * .42:.0f}" fill="url(#dotP)" opacity=".9"/>')
    b.append(f'<circle cx="{sx + sr + 6}" cy="{sy - 14}" r="2.4" fill="#FFFFFF"/>')
    # 나무(오른쪽): 줄기, 왼쪽 위로 뻗은 굵은 가지, 늘어진 잎가지
    tx = 668
    b.append(crown(668, 420, 84, 76, 16, 21))
    trunk = f"M{tx - 26},{G} C{tx - 18},{G - 120} {tx - 28},{G - 240} {tx - 14},{G - 330} L{tx + 24},{G - 330} C{tx + 18},{G - 220} {tx + 24},{G - 110} {tx + 34},{G} Z"
    b.append(f'<path d="{trunk}" fill="{PAPER}" stroke="{INK}" stroke-width="2.4"/><path d="{trunk}" fill="url(#hatch)"/>')
    br = f"M{tx - 8},{G - 280} C{tx - 130},{G - 320} {hand[0] + 130},{hand[1] - 40} {hand[0] - 70},{hand[1] - 56} L{hand[0] - 72},{hand[1] - 42} C{hand[0] + 120},{hand[1] - 22} {tx - 130},{G - 290} {tx - 6},{G - 254} Z"
    b.append(f'<path d="{br}" fill="{PAPER}" stroke="{INK}" stroke-width="2.2"/><path d="{br}" fill="url(#hatch)" opacity=".6"/>')
    for (fx, fy, a) in [(hand[0] - 40, hand[1] - 50, -30), (hand[0] + 70, hand[1] - 34, 20), (hand[0] + 150, hand[1] - 10, -25), (hand[0] + 220, hand[1] + 22, 25), (hand[0] - 10, hand[1] - 40, 160), (hand[0] + 110, hand[1] - 20, 200), (hand[0] + 190, hand[1] + 8, 160)]:
        b.append(leaf(fx, fy, a, 18, 8))
    sx0, sy0 = hand[0] + 24, hand[1] - 42
    b.append(f'<path d="M{sx0},{sy0} C{sx0 + 4},{sy0 + 14} {hand[0] + 10},{hand[1] - 18} {hand[0] + 1},{hand[1] + 6}" stroke="{LIGHT}" stroke-width="2.4" fill="none"/>')
    for (fx, fy, a) in [(sx0 + 2, sy0 + 10, 55), (hand[0] + 8, hand[1] - 16, -55), (hand[0] + 2, hand[1] + 6, 140), (hand[0] + 1, hand[1] + 8, -140)]:
        b.append(leaf(fx, fy, a, 15, 6))
    # 땅(풀밭)과 전기 울타리
    b.append(f'<rect x="0" y="{G}" width="{W}" height="{H - G}" fill="#16294A"/><rect x="0" y="{G}" width="{W}" height="{H - G}" fill="url(#dotP)" opacity=".8"/>')
    b.append(f'<line x1="0" y1="{G}" x2="{W}" y2="{G}" stroke="{LIGHT}" stroke-width="1.5" opacity=".7"/>')
    b.append("".join(f'<path d="M{x},{G + 2} l4,-12 l4,12" stroke="{LIGHT}" stroke-width="1.2" fill="none" opacity=".55"/>' for x in range(10, W, 31)))
    fx_ = [tx - 76, tx - 24, tx + 52, tx + 100]
    b.append("".join(f'<rect x="{x - 3}" y="{G - 64}" width="6" height="64" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>' for x in fx_))
    for f in (0.25, 0.55, 0.85):
        yy = G - 64 * (1 - f)
        b.append(f'<polyline points="{" ".join(f"{x},{yy:.0f}" for x in fx_)}" fill="none" stroke="{LIGHT}" stroke-width="1.4"/>')
    b.append(bolt(tx - 50, G - 46, 1.15))
    # 바위 단 + 받침 고릴라 + 올라선 고릴라(둘 다 다 자란 암컷: 은빛 등·머리 볏 없음, 몸집 비슷)
    b.append(rock(LX - 120, LX + 145, RT, G, fill="url(#dotG)"))
    b.append(gorilla_quad(LX, RT, LS, halo=LIGHT))
    b.append(gorilla_stand(AX, back_y + 1, AS, arm="up", halo=LIGHT))
    return svg("n2_cover", W, H, "".join(b))

ART["n2_cover"] = cover()


# ---------------------------------------------------------------- S1: 약 4.5m는 얼마나 높을까 (고릴라는 그리지 않음)
def person(cx, top, h, fill="url(#dotN)", stroke=INK):
    k = h / 150
    return (f'<g transform="translate({cx},{top}) scale({k:.3f})" stroke="{stroke}" stroke-width="{1.8 / k:.2f}" stroke-linejoin="round">'
            f'<circle cx="0" cy="13" r="12" fill="{PAPER}"/>'
            f'<path d="M-20,30 Q0,24 20,30 L24,84 L14,86 L12,148 L2,148 L0,96 L-2,148 L-12,148 L-14,86 L-24,84 Z" fill="{PAPER}"/>'
            f'<path d="M-20,30 Q0,24 20,30 L24,84 L14,86 L12,148 L2,148 L0,96 L-2,148 L-12,148 L-14,86 L-24,84 Z" fill="{fill}"/></g>')


def fig_s1():
    W, H, G, K = 720, 600, 560, 100          # 1m = 100
    Y = lambda m: G - m * K
    b = []
    b.append(f'<line x1="20" y1="{G}" x2="{W - 20}" y2="{G}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(f'<rect x="20" y="{G}" width="{W - 40}" height="14" fill="url(#hatch)"/>')
    # 눈금자 0~5m
    rx = 70
    b.append(f'<rect x="{rx - 14}" y="{Y(5)}" width="14" height="{5 * K}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    for i in range(11):
        m = i / 2
        L = 14 if i % 2 == 0 else 8
        b.append(line(rx - 14, Y(m), rx - 14 + L, Y(m), INK, 1.6 if i % 2 == 0 else 1.1))
        if i % 2 == 0: b.append(t(rx - 22, Y(m) + 6, str(int(m)), 18, INK, "end"))
    b.append(t(rx - 22, Y(5) - 26, "(m)", 18, GRAY, "end", 500))
    # 농구 골대(링 3.05m, 백보드 2.9~3.95m)
    px = 170
    b.append(f'<rect x="{px - 6}" y="{Y(3.3)}" width="12" height="{3.3 * K}" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>')
    b.append(f'<path d="M{px},{Y(3.25)} L{px + 52},{Y(3.25)} M{px},{Y(3.0)} L{px + 52},{Y(3.25)}" stroke="{INK}" stroke-width="3" fill="none"/>')
    b.append(f'<rect x="{px + 52}" y="{Y(3.95)}" width="8" height="{1.05 * K}" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>')
    b.append(f'<line x1="{px + 60}" y1="{Y(3.05)}" x2="{px + 105}" y2="{Y(3.05)}" stroke="{RED}" stroke-width="4"/>')
    b.append(f'<path d="M{px + 62},{Y(3.05)} L{px + 70},{Y(2.65)} L{px + 95},{Y(2.65)} L{px + 103},{Y(3.05)} M{px + 70},{Y(2.65)} L{px + 84},{Y(3.05)} L{px + 95},{Y(2.65)} M{px + 66},{Y(2.85)} L{px + 99},{Y(2.85)}" stroke="{INK}" stroke-width="1" fill="none"/>')
    # 사람 셋(각 1.5m)
    cx = 400
    for i in range(3):
        b.append(person(cx, Y(1.5 * (i + 1)), 1.5 * K))
    # 4.5m 잎가지
    b.append(f'<path d="M{cx + 120},{Y(5.05)} C{cx + 60},{Y(4.95)} {cx + 10},{Y(4.8)} {cx},{Y(4.5)}" stroke="{INK}" stroke-width="2.2" fill="none"/>')
    for (fx, fy, a) in [(cx + 60, Y(4.93), 50), (cx + 30, Y(4.83), -60), (cx + 6, Y(4.62), 60), (cx + 2, Y(4.52), -150), (cx - 2, Y(4.5), 150)]:
        b.append(leaf(fx, fy, a, 16, 7))
    # 기준선
    b.append(line(rx, Y(3.05), W - 30, Y(3.05), NAVY, 2, "8 6"))
    b.append(line(rx, Y(4.5), W - 30, Y(4.5), RED, 2.4, "8 6"))
    b.append(t(W - 30, Y(4.5) - 12, "땅에서 약 4.5m", 20, RED, "end"))
    b.append(t(W - 30, Y(3.05) + 28, "농구 링 3m 5cm", 20, NAVY, "end"))
    # 1m 45cm 치수선
    dx = 600
    b.append(line(dx, Y(4.5) + 4, dx, Y(3.05) - 4, INK, 1.6, mk="arr")); b.append(line(dx, Y(3.05) - 4, dx, Y(4.5) + 4, INK, 1.6, mk="arr"))
    b.append(tb(dx - 14, (Y(4.5) + Y(3.05)) / 2 + 7, "1m 45cm", 20, INK, "end"))
    # 사람 셋 괄호
    bx = cx + 40
    for i in range(3):
        y0, y1 = Y(1.5 * i) - 3, Y(1.5 * (i + 1)) + 3
        b.append(f'<path d="M{bx},{y0} q8,0 8,-8 L{bx + 8},{y1 + 8} q0,-8 -8,-8" stroke="{NAVY}" stroke-width="1.6" fill="none"/>')
    b.append(t(bx + 18, Y(1.5) - 2, "1m 50cm × 3", 20, NAVY))
    return svg("n2_gorilla_s1", W, H, "".join(b))

ART["n2_gorilla_s1"] = fig_s1()


# ---------------------------------------------------------------- S2: '도구'와 '협력' (두 줄 세 칸, 표정 없는 실루엣)
def quad_sq(x, y, s, fill, flip=False, sq=0.62, far=None, stroke=None):
    """눌려 엎드린 자세(세로로 납작하게)."""
    sx = -s if flip else s
    st = stroke or fill
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({sx:.3f},{s * sq:.3f})">'
            f'<path d="{QUAD_FAR}" fill="{far or fill}" stroke="{st}" stroke-width="{1.4 / s:.1f}" vector-effect="non-scaling-stroke"/><path d="{QUAD_BODY}" fill="{fill}" stroke="{st}" stroke-width="1.4" vector-effect="non-scaling-stroke"/></g>')


def fig_s2():
    W, H = 720, 560
    b = []
    cw, xs = 200, [10, 215, 420]
    rows = [(18, "도구로 쓴 경우(이번 일과 달라요)", FAINT), (288, "리샤와 아멜리아(2025년 영상)", INK)]
    for ry, title, col in rows:
        b.append(t(14, ry + 22, title, 20, col))
        for i, x in enumerate(xs):
            b.append(f'<rect x="{x}" y="{ry + 36}" width="{cw}" height="214" fill="{PAPER}" stroke="{col}" stroke-width="1.4"/>')
            b.append(f'<circle cx="{x + 18}" cy="{ry + 56}" r="13" fill="{col}"/>' + t(x + 18, ry + 63, "①②③"[i], 18, PAPER, "middle"))
    # 윗줄(옅은 색): A = 회색빛 남색, B = 더 옅은 색
    gy = 18 + 36 + 196
    A, Bf = FAINT, "#C9D0D8"
    # ① 끌어옴: A가 팔로 B를 끌어오고, 끌려오는 B에 남색 화살표
    x = xs[0]
    b.append(gorilla_quad(x + 58, gy, 0.36, fill=Bf, far=Bf, detail=False, stroke=FAINT))
    b.append(gorilla_stand(x + 150, gy, 0.42, flip=True, fill=A, arm="push", detail=False))
    b.append(line(x + 24, gy - 92, x + 86, gy - 92, NAVY, 2.4, mk="arrN"))
    # ② 눌러 엎드리게 함
    x = xs[1]
    b.append(quad_sq(x + 78, gy, 0.36, Bf, sq=0.55, stroke=FAINT))
    b.append(gorilla_stand(x + 142, gy, 0.42, flip=True, fill=A, arm="push", detail=False))
    b.append(line(x + 86, gy - 110, x + 86, gy - 66, NAVY, 2.4, mk="arrN"))
    # ③ 그 등에 올라탐
    x = xs[2]
    b.append(quad_sq(x + 96, gy, 0.38, Bf, sq=0.55, stroke=FAINT))
    b.append(gorilla_stand(x + 86, gy - 125 * 0.38 * 0.55, 0.38, fill=A, arm="down", detail=False, halo=PAPER))
    # 아랫줄(진한 색): 리샤 = 잉크, 아멜리아 = 남색
    gy = 288 + 36 + 196
    Am = NAVY
    # ① 리샤가 스스로 걸어 다가감(화살표 = 스스로 가는 방향)
    x = xs[0]
    b.append(gorilla_quad(x + 60, gy, 0.36, detail=False))
    b.append(gorilla_stand(x + 172, gy, 0.42, flip=True, fill=Am, arm="down", detail=False))
    b.append(line(x + 26, gy - 88, x + 100, gy - 88, NAVY, 2.4, mk="arrN"))
    # ② 낮은 바위 단 위에서 등을 내주고 네 발로 버팀
    x = xs[1]
    b.append(rock(x + 52, x + 158, gy - 18, gy))
    b.append(gorilla_quad(x + 104, gy - 18, 0.36, detail=False))
    b.append(gorilla_stand(x + 30, gy, 0.42, fill=Am, arm="down", detail=False))
    # ③ 올라선 아멜리아가 위의 가지를 꺾음
    x = xs[2]
    b.append(rock(x + 20, x + 132, gy - 18, gy))
    b.append(gorilla_quad(x + 72, gy - 18, 0.36, detail=False))
    ay = gy - 18 - 133 * 0.36
    b.append(gorilla_stand(x + 66, ay, 0.36, fill=Am, arm="up", detail=False, halo=PAPER))
    hx, hy = x + 66 + 14 * 0.36, ay - 258 * 0.36
    b.append(f'<path d="M{x + 200},{hy - 26} L{hx + 14},{hy - 6} M{hx + 8},{hy - 4} l-6,6 l7,3 l-5,7" stroke="{INK}" stroke-width="2.4" fill="none"/>')
    b.append(leaf(x + 170, hy - 20, -40, 14, 6) + leaf(x + 140, hy - 14, 40, 14, 6))
    # 도장
    cx, cy = 668, 418
    b.append(f'<g transform="rotate(-10 {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="48" fill="{PAPER}" stroke="{RED}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="41" fill="none" stroke="{RED}" stroke-width="1.2"/>'
             + t(cx, cy - 16, "연구진의", 18, RED, "middle") + t(cx, cy + 6, "해석:", 18, RED, "middle") + t(cx, cy + 34, "협력", 24, RED, "middle", 900) + "</g>")
    b.append(line(624, 418, 640, 418, RED, 2))
    return svg("n2_gorilla_s2", W, H, "".join(b))

ART["n2_gorilla_s2"] = fig_s2()


# ---------------------------------------------------------------- 별 공통
def spiral(cx, cy, r0, r1, turns, a0=-math.pi / 2, n=None):
    """r0(바깥)에서 r1(안쪽)으로 정확히 turns바퀴 감기는 나선(시계 방향). 끝점도 돌려 줌."""
    n = n or int(turns * 90)
    pts = []
    for i in range(n + 1):
        f = i / n; a = a0 + 2 * math.pi * turns * f; r = r0 + (r1 - r0) * f
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), pts[-1], pts


def fuzzy_star(cx, cy, R, seed=5, base="#F2D6CB", core=0.0, edge=1.25, n=900):
    """가운데는 빽빽하고 바깥으로 갈수록 성긴 빨강 망점. 가장자리는 또렷한 선 없이 풀어짐."""
    r = random.Random(seed)
    gid = f"fz{seed}"
    out = [f'<radialGradient id="{gid}"><stop offset="0" stop-color="{base}"/><stop offset=".72" stop-color="{base}"/><stop offset="1" stop-color="{base}" stop-opacity="0"/></radialGradient>'
           f'<circle cx="{cx}" cy="{cy}" r="{R * 1.08:.1f}" fill="url(#{gid})"/>']
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * .7:.1f}" fill="url(#dotRd)" opacity=".55"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * .82:.1f}" fill="url(#dotR)" opacity=".7"/>')
    for _ in range(n):
        rr = R * (0.55 + 0.7 * r.random() ** 0.8)
        if rr > R * edge: continue
        a = r.uniform(0, 2 * math.pi)
        out.append(f'<circle cx="{cx + rr * math.cos(a):.1f}" cy="{cy + rr * math.sin(a):.1f}" r="{r.choice([0.9, 1.2, 1.5])}" fill="{RED}" opacity="{max(.15, 1.1 - rr / R * .75):.2f}"/>')
    return "".join(out)


# ---------------------------------------------------------------- S3: 태양과 빅 바오 크기 견주기 (1 : 350)
def fig_s3():
    W, H, G, K = 720, 580, 500, 85       # 1m = 85
    Y = lambda m: G - m * K
    b = []
    b.append(f'<line x1="14" y1="{G}" x2="{W - 14}" y2="{G}" stroke="{INK}" stroke-width="2.5"/><rect x="14" y="{G}" width="{W - 28}" height="12" fill="url(#hatch)"/>')
    # 4.5m 고릴라 기사의 가지(옅은 빨강 점선)
    b.append(line(14, Y(4.5), W - 14, Y(4.5), RED, 1.8, "6 6"))
    b.append(f'<path d="M{W - 14},{Y(4.5) - 40} C{W - 50},{Y(4.5) - 30} {W - 70},{Y(4.5) - 20} {W - 78},{Y(4.5)}" stroke="{INK}" stroke-width="2" fill="none"/>')
    b.append(leaf(W - 78, Y(4.5), 160, 14, 6) + leaf(W - 76, Y(4.5) - 4, -150, 14, 6) + leaf(W - 50, Y(4.5) - 28, 50, 14, 6))
    b.append(t(W - 100, Y(4.5) - 12, "고릴라 기사의 가지: 땅에서 약 4.5m", 18, RED, "end"))
    # 빅 바오: 지름 3.5m = 태양(1cm)의 350배, 바닥에 닿음
    D = 3.5 * K; bx = W - 24 - D / 2; by = G - D / 2
    b.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{D / 2:.1f}" fill="#F4DCD2" stroke="{RED}" stroke-width="2.5"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="{D / 2:.1f}" fill="url(#dotR)"/>')
    b.append(tb(bx, by - 8, "빅 바오 = 지름 3m 50cm 공", 18, INK, "middle"))
    b.append(tb(bx, by + 26, "(태양의 약 350배)", 18, RED, "middle"))
    # 농구 골대(같은 축척, 링 3.05m)
    px = bx - D / 2 - 100
    b.append(f'<rect x="{px - 5:.1f}" y="{Y(3.3):.1f}" width="10" height="{3.3 * K:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<path d="M{px},{Y(3.25)} L{px + 40},{Y(3.25)} M{px},{Y(3.02)} L{px + 40},{Y(3.25)}" stroke="{INK}" stroke-width="2.5" fill="none"/>')
    b.append(f'<rect x="{px + 40:.1f}" y="{Y(3.95):.1f}" width="7" height="{1.05 * K:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<line x1="{px + 47:.1f}" y1="{Y(3.05):.1f}" x2="{px + 85:.1f}" y2="{Y(3.05):.1f}" stroke="{RED}" stroke-width="3.5"/>')
    b.append(f'<path d="M{px + 49},{Y(3.05)} L{px + 56},{Y(2.7)} L{px + 77},{Y(2.7)} L{px + 84},{Y(3.05)} M{px + 56},{Y(2.7)} L{px + 67},{Y(3.05)} L{px + 77},{Y(2.7)}" stroke="{INK}" stroke-width="1" fill="none"/>')
    b.append(line(px + 85, Y(3.05), bx + D / 2 + 6, Y(3.05), NAVY, 1.8, "7 5"))
    b.append(t(px + 44, Y(3.95) - 12, "농구 링 3m 5cm", 18, NAVY, "middle"))
    # 태양 자리: 이 축척에서 지름 0.85px라 점과 지시선만
    sx = 40
    b.append(f'<circle cx="{sx}" cy="{G - 0.5}" r="1.2" fill="{INK}"/><circle cx="{sx}" cy="{G - 0.5}" r="7" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    # 돋보기(크게 보기): 태양(1cm)과 리틀 바오(태양보다 조금 작음)
    mx, my, mr = 130, 228, 92
    b.append(line(sx, G - 8, sx, my + math.sqrt(mr ** 2 - (mx - sx) ** 2) + 2, INK, 1.4, "4 4"))
    b.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#fff" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<line x1="{mx + mr * .72:.0f}" y1="{my + mr * .72:.0f}" x2="{mx + mr * .72 + 24:.0f}" y2="{my + mr * .72 + 24:.0f}" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>')
    b.append(f'<circle cx="{mx - 36}" cy="{my - 8}" r="30" fill="#F4DCD2" stroke="{RED}" stroke-width="2"/><circle cx="{mx - 36}" cy="{my - 8}" r="30" fill="url(#dotR)"/>')
    b.append(f'<circle cx="{mx + 40}" cy="{my - 2}" r="24" fill="#E3E8EE" stroke="{NAVY}" stroke-width="2"/><circle cx="{mx + 40}" cy="{my - 2}" r="24" fill="url(#dotN)"/>')
    b.append(t(mx - 36, my + 46, "태양", 18, INK, "middle") + t(mx + 40, my + 46, "리틀 바오", 18, NAVY, "middle"))
    b.append(t(mx + mr + 12, my - 50, "크게 보기", 18, GRAY, "start", 700))
    b.append(tl(sx + 20, my + mr + 46, ["태양: 지름 1cm 구슬", "리틀 바오: 태양보다 조금 작음"], 18, INK, "start", 500, 1.35))
    b.append(t(16, 34, "태양 = 지름 1cm 구슬이라면", 22, INK))
    b.append(t(W / 2, H - 22, "관측 자료에 맞춘 계산(모형)에서 나온 어림값이에요.", 18, GRAY, "middle", 500))
    return svg("n2_merger_s3", W, H, "".join(b))

ART["n2_merger_s3"] = fig_s3()


# ---------------------------------------------------------------- g3 대신: 큰 별의 바깥 기체 속으로 일곱 바퀴 파고드는 작은 별
def fig_g3():
    W, H = 720, 480
    cx, cy, R = 360, 240, 160
    b = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/><rect width="{W}" height="{H}" fill="url(#dot)" opacity=".3"/>', stars(0, 0, W, H, 70, 31, LIGHT, 1.5)]
    # 먼지 띠(성긴 밝은 망점)
    r = random.Random(9)
    for _ in range(420):
        rr = r.uniform(R * 1.08, R * 1.42); a = r.uniform(0, 2 * math.pi)
        b.append(f'<circle cx="{cx + rr * math.cos(a) * 1.08:.1f}" cy="{cy + rr * math.sin(a) * .9:.1f}" r="{r.choice([.8, 1.1])}" fill="{LIGHT}" opacity="{r.uniform(.15, .5):.2f}"/>')
    b.append(fuzzy_star(cx, cy, R, seed=4, n=1600))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{PAPER}" stroke="{RED}" stroke-width="1.5"/><circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{PAPER}" stroke-width="1" stroke-dasharray="2 3"/>')
    d, end, pts = spiral(cx, cy, R * .94, 44, 7, a0=math.pi * 1.1)
    b.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.1" opacity=".8"/>')
    # 작은 별(흰 점, 큰 별 지름의 30분의 1보다 작게: 지름 9 < 320/30)
    ex, ey = end
    # 지나온 자리의 물결 자국
    i0 = len(pts) - 1
    for k, back in enumerate((10, 18, 26)):
        x0, y0 = pts[i0 - back]; x1, y1 = pts[i0 - back + 4]
        ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        for sgn in (1, -1):
            ox, oy = math.cos(ang) * (6 + k * 2) * sgn, math.sin(ang) * (6 + k * 2) * sgn
            b.append(f'<path d="M{x0 + ox:.1f},{y0 + oy:.1f} Q{(x0 + x1) / 2 + ox * 1.3:.1f},{(y0 + y1) / 2 + oy * 1.3:.1f} {x1 + ox:.1f},{y1 + oy:.1f}" stroke="{INK}" stroke-width="1.2" fill="none" opacity="{.8 - k * .2:.1f}"/>')
    b.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="11" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="2 3"/>')
    b.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.2" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>')
    # 라벨
    b.append(line(150, 70, cx - R * .62, cy - R * .62, LIGHT, 1.3))
    b.append(tb(14, 62, "빅 바오의 바깥 기체(공동 외피)", 18, INK))
    b.append(line(ex - 10, ey + 6, 236, 400, LIGHT, 1.3))
    b.append(tb(130, 420, "리틀 바오", 18, NAVY))
    b.append(line(cx + 22, cy + 6, 560, 330, LIGHT, 1.3))
    b.append(tb(560, 346, "중심핵", 18, INK))
    b.append(tb(W - 14, 62, "일곱 바퀴, 약 7년", 18, RED, "end"))
    b.append(line(W - 120, 72, cx + R * .7, cy - R * .5, LIGHT, 1.3))
    return svg("n2_merger_g3", W, H, "".join(b))

ART["n2_merger_g3"] = fig_g3()


# ---------------------------------------------------------------- S4: 두 별이 하나가 되기까지 네 단계(2×2)
def fig_s4():
    W, H = 720, 660
    PW, PH = 345, 290
    pos = [(10, 10), (365, 10), (10, 312), (365, 312)]
    b = []
    labels = [["수천 년 동안", "서로를 돌던 두 별"], ["2018년 무렵부터 약 7년,", "일곱 바퀴"], ["2025년 10월 폭발:", "바깥 껍질 일부가 날아감"], ["하나가 된 것으로", "보이는 바오"]]
    for i, (x, y) in enumerate(pos):
        b.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
        b.append(f'<circle cx="{x + 20}" cy="{y + 22}" r="14" fill="{INK}"/>' + t(x + 20, y + 29, "①②③④"[i], 19, PAPER, "middle"))
        b.append(tl(x + PW / 2, y + PH - 44, labels[i], 18, RED if i == 2 else INK, "middle", 700, 1.3))
    # ① 서로를 돌던 두 별: 둘레에 옅은 먼지
    x, y = pos[0]; cx, cy = x + PW / 2 - 20, y + 112
    r = random.Random(2)
    for _ in range(160):
        rr = r.uniform(108, 124); a = r.uniform(0, 2 * math.pi)
        b.append(f'<circle cx="{cx + 20 + rr * math.cos(a):.1f}" cy="{cy + rr * math.sin(a) * .7:.1f}" r="1" fill="{GRAY}" opacity=".6"/>')
    b.append(f'<ellipse cx="{cx + 12}" cy="{cy}" rx="100" ry="34" fill="none" stroke="{NAVY}" stroke-width="1.4" stroke-dasharray="5 5"/>')
    b.append(fuzzy_star(cx, cy, 42, seed=1, n=200, edge=1.1))
    b.append(f'<circle cx="{cx + 108}" cy="{cy - 14}" r="4" fill="{NAVY}"/>')
    b.append(f'<path d="M{cx + 70},{cy + 34} q16,-4 28,-14" stroke="{NAVY}" stroke-width="1.6" fill="none" marker-end="url(#arrN)"/>')
    # ② 바깥 기체 속에서 일곱 바퀴 나선
    x, y = pos[1]; cx, cy = x + PW / 2, y + 116
    b.append(fuzzy_star(cx, cy, 94, seed=3, n=600, edge=1.12))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{PAPER}" stroke="{RED}" stroke-width="1.2"/>')
    d, end, _ = spiral(cx, cy, 88, 18, 7, a0=math.pi * 1.1)
    b.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    b.append(f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="3.6" fill="{NAVY}" stroke="{PAPER}" stroke-width="1"/>')
    # ③ 폭발: 가운데가 밝아지고 가장 바깥 껍질이 사방으로 얇게 날아감(몸통은 그대로)
    x, y = pos[2]; cx, cy = x + PW / 2, y + 112
    b.append(f'<circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="10 7"/>')
    for k in range(12):
        a = 2 * math.pi * k / 12 + .13
        b.append(line(cx + 68 * math.cos(a), cy + 68 * math.sin(a), cx + 88 * math.cos(a), cy + 88 * math.sin(a), RED, 1.8, mk="arrR"))
    b.append(fuzzy_star(cx, cy, 54, seed=6, n=260, edge=1.08))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="#FFFFFF" opacity=".95"/>')
    for k in range(8):
        a = 2 * math.pi * k / 8
        b.append(line(cx + 10 * math.cos(a), cy + 10 * math.sin(a), cx + 26 * math.cos(a), cy + 26 * math.sin(a), RED, 2.2))
    # ④ 하나가 된 별, 위아래 두 방향으로 퍼지는 먼지
    x, y = pos[3]; cx, cy = x + PW / 2, y + 112
    for sgn in (-1, 1):
        b.append(f'<path d="M{cx - 14},{cy + sgn * 30} C{cx - 70},{cy + sgn * 70} {cx - 50},{cy + sgn * 104} {cx},{cy + sgn * 98} C{cx + 50},{cy + sgn * 104} {cx + 70},{cy + sgn * 70} {cx + 14},{cy + sgn * 30} Z" fill="url(#dot)" stroke="{GRAY}" stroke-width="1" stroke-dasharray="3 3"/>')
        b.append(line(cx, cy + sgn * 50, cx, cy + sgn * 92, INK, 1.6, mk="arr"))
    b.append(fuzzy_star(cx, cy, 40, seed=8, n=180, edge=1.08))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{PAPER}" stroke="{RED}" stroke-width="1.2"/>')
    b.append(t(W / 2, H - 16, "크기 비율은 실제와 달라요. 작은 별은 훨씬 더 작아요.", 18, GRAY, "middle", 500))
    return svg("n2_merger_s4", W, H, "".join(b))

ART["n2_merger_s4"] = fig_s4()


# ---------------------------------------------------------------- S5: 바오 연표(세로판 = 휴대폰, 가로판 = PC)
S5 = [("2018년 전까지", ["밝기가 늘 같았어요"], NAVY, ["밝기가", "늘 같았어요"]),
      ("2018년 무렵", ["작은 별이 큰 별 겉면에 닿고,", "조금씩 밝아지기 시작"], NAVY, ["작은 별이 큰 별", "겉면에 닿고,", "조금씩 밝아지기", "시작"]),
      ("2023년 2월", ["니오와이즈 자료에서 눈에 띔"], NAVY, ["니오와이즈", "자료에서 눈에 띔"]),
      ("2025년 10월", ["폭발"], RED, ["폭발"]),
      ("2025년 12월 24일", ["웹 망원경 관측"], NAVY, ["웹 망원경 관측"]),
      ("2026년 11월 18일", ["《네이처》에 논문"], NAVY, ["《네이처》에", "논문"])]


def fig_s5v():
    W = 600; top = 40; gap = 104
    H = top + gap * 5 + 150
    lx = 170
    ys = [top + 20 + gap * i for i in range(6)]
    b = [line(lx, ys[0] - 20, lx, ys[-1] + 20, INK, 3)]
    for (d, desc, c, _), y in zip(S5, ys):
        b.append(f'<circle cx="{lx}" cy="{y}" r="{13 if c == RED else 10}" fill="{c}" stroke="{PAPER}" stroke-width="3"/>')
        b.append(t(lx + 30, y + 8, d, 23, c, "start", 900))
        b.append(tl(lx + 30, y + 40, desc, 20, INK, "start", 500, 1.3))
    # ②~④: 약 7년, 일곱 바퀴
    bx = lx - 34
    b.append(f'<path d="M{bx + 12},{ys[1]} L{bx},{ys[1]} L{bx},{ys[3]} L{bx + 12},{ys[3]}" stroke="{RED}" stroke-width="2.2" fill="none"/>')
    b.append(tl(bx - 12, (ys[1] + ys[3]) / 2 - 6, ["약 7년,", "일곱 바퀴"], 20, RED, "end", 700, 1.3))
    b.append(tl(W / 2, ys[-1] + 96, ["이 빛은 약 250만 년 전에", "바오를 떠난 빛이에요."], 20, GRAY, "middle", 500, 1.35))
    return svg("n2_merger_s5", W, H, "".join(b))


def fig_s5h():
    W, H = 960, 420
    y = 150; xs = [80 + 160 * i for i in range(6)]
    b = [line(xs[0] - 50, y, xs[-1] + 50, y, INK, 3, mk="arr")]
    for (d, desc, c, hl), x in zip(S5, xs):
        b.append(f'<circle cx="{x}" cy="{y}" r="{13 if c == RED else 10}" fill="{c}" stroke="{PAPER}" stroke-width="3"/>')
        dl = [d] if len(d) < 10 else [d.split("년 ")[0] + "년", d.split("년 ")[1]]
        b.append(tl(x, y + 46, dl, 20, c, "middle", 900, 1.3))
        b.append(tl(x, y + 46 + 26 * len(dl) + 4, hl, 18, INK, "middle", 500, 1.3))
    b.append(f'<path d="M{xs[1]},{y - 26} L{xs[1]},{y - 40} L{xs[3]},{y - 40} L{xs[3]},{y - 26}" stroke="{RED}" stroke-width="2.2" fill="none"/>')
    b.append(t((xs[1] + xs[3]) / 2, y - 52, "약 7년, 일곱 바퀴", 20, RED, "middle"))
    b.append(t(W / 2, H - 24, "이 빛은 약 250만 년 전에 바오를 떠난 빛이에요.", 18, GRAY, "middle", 500))
    return svg("n2_merger_s5_h", W, H, "".join(b))

ART["n2_merger_s5"] = fig_s5v()
ART["n2_merger_s5_h"] = fig_s5h()


# ---------------------------------------------------------------- S6: 2배로 쌓이는 겹(1, 2, 4, 8, 16)
def stack(x, base, w, n, th, fill_a=PAPER, fill_b="url(#dotR)", rounded=True):
    """옆에서 본 종이 더미: n겹, 겹 하나 두께 th. 오른쪽 끝은 접힌 모서리처럼 둥글게."""
    h = n * th; top = base - h
    rr = min(h / 2, 16) if rounded else 0
    out = [f'<path d="M{x},{top} L{x + w - rr},{top} Q{x + w},{top} {x + w},{top + rr} L{x + w},{base - rr} Q{x + w},{base} {x + w - rr},{base} L{x},{base} Z" fill="{fill_a}"/>']
    for i in range(n):
        if i % 2 == 0:
            out.append(f'<rect x="{x}" y="{base - (i + 1) * th:.1f}" width="{w - rr:.1f}" height="{th:.1f}" fill="{fill_b}" opacity=".9"/>')
    for i in range(1, n):
        yy = base - i * th
        out.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w - rr * .3:.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<path d="M{x},{top} L{x + w - rr},{top} Q{x + w},{top} {x + w},{top + rr} L{x + w},{base - rr} Q{x + w},{base} {x + w - rr},{base} L{x},{base} Z" fill="none" stroke="{INK}" stroke-width="2"/>')
    return "".join(out)


def fig_s6():
    W, H, base, th = 720, 420, 330, 17
    b = []
    xs = [22 + 142 * i for i in range(5)]
    for i, x in enumerate(xs):
        n = 2 ** i
        b.append(stack(x, base, 96, n, th))
        b.append(t(x + 48, base + 36, f"{i}번 {n}겹", 20, INK, "middle"))
        if i < 4:
            yy = base - 2 ** i * th / 2 - 4
            b.append(f'<path d="M{x + 104},{base - 30} Q{x + 121},{base - 70} {x + 136},{base - 30}" stroke="{RED}" stroke-width="2.2" fill="none" marker-end="url(#arrR)"/>')
            b.append(t(x + 120, base - 78, "×2", 20, RED, "middle", 900))
    b.append(f'<line x1="10" y1="{base}" x2="{W - 10}" y2="{base}" stroke="{INK}" stroke-width="2"/>')
    b.append(t(W / 2, H - 24, "겹 하나의 두께는 모두 같아요. 더미의 높이도 2배씩 늘어요.", 18, GRAY, "middle", 500))
    return svg("n2_folding_s6", W, H, "".join(b))

ART["n2_folding_s6"] = fig_s6()


# ---------------------------------------------------------------- S7: 10번, 20번, 42번 (칸마다 줄인 정도가 다름)
def fig_s7():
    W, H = 720, 560
    PW, top, ph = 230, 56, 420
    xs = [8, 245, 482]
    b = [t(W / 2, 36, "칸마다 줄인 정도가 달라요", 22, RED, "middle", 900)]
    for x in xs:
        b.append(f'<rect x="{x}" y="{top}" width="{PW}" height="{ph}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    # 1칸: 30cm 자 + 102.4mm 종이 더미
    x = xs[0]; g = top + ph - 76; k = 10.5            # 1cm = 10.5
    rx = x + 34
    b.append(f'<rect x="{rx}" y="{g - 30 * k}" width="30" height="{30 * k}" fill="#F3E6C4" stroke="{INK}" stroke-width="1.6"/>')
    for c in range(31):
        L = 14 if c % 5 == 0 else 7
        b.append(line(rx + 30 - L, g - c * k, rx + 30, g - c * k, INK, 1.2 if c % 5 == 0 else .8))
        if c % 10 == 0: b.append(t(rx - 6, g - c * k + 6, str(c), 18, INK, "end", 500))
    b.append(t(rx + 15, g - 30 * k - 10, "(cm)", 18, GRAY, "middle", 500))
    hh = 102.4 / 10 * k
    b.append(f'<rect x="{rx + 44}" y="{g - hh:.1f}" width="70" height="{hh:.1f}" fill="#F4DCD2" stroke="{RED}" stroke-width="2"/>')
    b.append("".join(f'<line x1="{rx + 44}" y1="{g - hh + i * hh / 22:.1f}" x2="{rx + 114}" y2="{g - hh + i * hh / 22:.1f}" stroke="{RED}" stroke-width=".7" opacity=".7"/>' for i in range(1, 22)))
    b.append(line(rx + 30, g - 10 * k, rx + 124, g - 10 * k, INK, 1, "3 3"))
    b.append(t(rx + 79, g - hh - 12, "10.2cm", 18, RED, "middle"))
    b.append(line(x, g, x + PW, g, INK, 1.6))
    b.append(tl(x + PW / 2, g + 30, ["10번 · 1,024겹", "약 10cm"], 18, INK, "middle", 700, 1.3))
    # 2칸: 100m 막대와 약 104.86m 종이 기둥
    x = xs[1]; g = top + ph - 76; k = 2.6
    hb, hp = 100 * k, 104.8576 * k
    b.append(f'<rect x="{x + 40}" y="{g - hb:.1f}" width="44" height="{hb:.1f}" fill="url(#dotN)" stroke="{NAVY}" stroke-width="2"/>')
    b.append(f'<rect x="{x + 140}" y="{g - hp:.1f}" width="44" height="{hp:.1f}" fill="#F4DCD2" stroke="{RED}" stroke-width="2"/><rect x="{x + 140}" y="{g - hp:.1f}" width="44" height="{hp:.1f}" fill="url(#dotR)"/>')
    b.append(line(x + 84, g - hb, x + 140, g - hb, INK, 1, "3 3"))
    b.append(tl(x + 62, g - hb - 36, ["100m 달리기", "길이"], 18, NAVY, "middle", 700, 1.2))
    b.append(t(x + 162, g - hp - 12, "약 105m", 18, RED, "middle"))
    b.append(line(x, g, x + PW, g, INK, 1.6))
    b.append(tl(x + PW / 2, g + 30, ["20번 · 약 105m", "(100m보다 조금 높아요)"], 18, INK, "middle", 700, 1.3))
    # 3칸: 지구에서 달(38만 4,400km)을 지나 약 44만 km
    x = xs[2]; g = top + ph - 76
    ex, ey = x + 30, g - 22
    ang = math.radians(-60)
    L_moon = 262; L_end = L_moon * 439804.65 / 384400
    mx_, my_ = ex + L_moon * math.cos(ang), ey + L_moon * math.sin(ang)
    qx, qy = ex + L_end * math.cos(ang), ey + L_end * math.sin(ang)
    b.append(line(ex, ey, qx, qy, RED, 3, mk="arrR"))
    b.append(f'<circle cx="{ex}" cy="{ey}" r="9" fill="url(#dotN)" stroke="{NAVY}" stroke-width="2"/>')
    b.append(f'<circle cx="{mx_:.1f}" cy="{my_:.1f}" r="5" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    b.append(t(ex + 16, ey + 8, "지구", 18, NAVY))
    b.append(t(mx_ + 12, my_ + 18, "달", 18, INK))
    b.append(tl(x + 96, my_ + 96, ["달까지 약", "38만 4,400km"], 18, INK, "start", 500, 1.3))
    b.append(line(x + 150, my_ + 74, mx_ + 3, my_ + 8, INK, 1))
    b.append(t(qx - 14, qy + 6, "약 44만 km", 18, RED, "end"))
    b.append(line(x, g, x + PW, g, INK, 1.6))
    b.append(tl(x + PW / 2, g + 30, ["42번 · 약 44만 km", "(달을 지나가요)"], 18, INK, "middle", 700, 1.3))
    b.append(t(W / 2, H - 24, "종이 10장이 약 1mm라고 가정하고 계산했어요.", 18, GRAY, "middle", 500))
    return svg("n2_folding_s7", W, H, "".join(b))

ART["n2_folding_s7"] = fig_s7()


# ---------------------------------------------------------------- S8: 뒤집기 둘 = 돌리기 하나 (시뮬레이터와 같은 깃발)
POLE = [(0, -1.5), (0, 1.5)]
FLAG = [(0, -1.5), (1.3, -1), (0, -0.5)]


def flag(cx, cy, c, M=(1, 0, 0, 1), ghost=False):
    a, bb, cc, d = M
    P = lambda p: (cx + (a * p[0] + bb * p[1]) * c, cy + (cc * p[0] + d * p[1]) * c)
    p0, p1 = P(POLE[0]), P(POLE[1])
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in map(P, FLAG))
    if ghost:
        return (f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{FAINT}" stroke-width="3" stroke-dasharray="4 4"/>'
                f'<polygon points="{pts}" fill="none" stroke="{FAINT}" stroke-width="2" stroke-dasharray="4 4"/>')
    return (f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<polygon points="{pts}" fill="{RED}" stroke="{INK}" stroke-width="1.6"/><circle cx="{cx}" cy="{cy}" r="4.5" fill="{NAVY}"/>')


def fig_s8():
    W, H, c = 720, 640, 34
    PW, PH = 330, 270
    pos = {1: (14, 50), 2: (376, 50), 4: (14, 352), 3: (376, 352)}
    I, FR, FD, R2 = (1, 0, 0, 1), (-1, 0, 0, 1), (1, 0, 0, -1), (-1, 0, 0, -1)
    labels = {1: "① 처음", 2: "② 오른쪽으로 뒤집기", 3: "③ 아래쪽으로 뒤집기", 4: "④ 처음을 180° 돌리기"}
    b = []
    for k, (x, y) in pos.items():
        b.append(t(x + 4, y - 14, labels[k], 20, INK))
        b.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH - 40}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.6"/>')
        gx0 = x + PW / 2 - c * 4; gy0 = y + (PH - 40) / 2 - c * 3
        for i in range(9): b.append(line(gx0 + i * c, y + 4, gx0 + i * c, y + PH - 44, "#D9D3C6", 1))
        for j in range(7): b.append(line(x + 4, gy0 + j * c - c * 0, x + PW - 4, gy0 + j * c, "#D9D3C6", 1))
    ctr = {k: (x + PW / 2, y + (PH - 40) / 2) for k, (x, y) in pos.items()}
    # ① 처음
    b.append(flag(*ctr[1], c, I))
    # ② 오른쪽으로 뒤집기: 깃대를 지나는 세로 점선
    cx, cy = ctr[2]
    b.append(flag(cx, cy, c, I, ghost=True))
    b.append(line(cx, cy - c * 3, cx, cy + c * 3, NAVY, 2.4, "8 6"))
    b.append(flag(cx, cy, c, FR))
    # ③ 이어서 아래쪽으로 뒤집기: 깃대 가운데를 지나는 가로 점선
    cx, cy = ctr[3]
    b.append(flag(cx, cy, c, FR, ghost=True))
    b.append(line(cx - c * 4, cy, cx + c * 4, cy, NAVY, 2.4, "8 6"))
    b.append(flag(cx, cy, c, FD if False else (-1, 0, 0, -1)))
    # ④ 처음을 180° 돌리기: 가운데 점과 반 바퀴 굽은 화살표
    cx, cy = ctr[4]
    b.append(flag(cx, cy, c, I, ghost=True))
    rr = c * 2.1
    b.append(f'<path d="M{cx + rr * math.cos(math.radians(-70)):.1f},{cy + rr * math.sin(math.radians(-70)):.1f} A{rr},{rr} 0 0 1 {cx + rr * math.cos(math.radians(105)):.1f},{cy + rr * math.sin(math.radians(105)):.1f}" stroke="{NAVY}" stroke-width="2.6" fill="none" marker-end="url(#arrN)"/>')
    b.append(flag(cx, cy, c, R2))
    # 화살표와 '='
    (x1, y1), (x2, y2) = pos[1], pos[2]
    b.append(line(x1 + PW + 4, y1 + 115, x2 - 6, y2 + 115, INK, 2, mk="arr"))
    b.append(line(pos[2][0] + PW / 2, pos[2][1] + PH - 34, pos[3][0] + PW / 2, pos[3][1] - 40, INK, 2, mk="arr"))
    b.append(line(pos[1][0] + PW / 2, pos[1][1] + PH - 34, pos[4][0] + PW / 2, pos[4][1] - 40, INK, 2, mk="arr"))
    b.append(t((pos[4][0] + PW + pos[3][0]) / 2, pos[3][1] + 132, "=", 44, RED, "middle", 900))
    b.append(t(W / 2, H - 16, "③과 ④는 깃발의 모양과 자리가 똑같아요.", 18, GRAY, "middle", 500))
    return svg("n2_snow_s8", W, H, "".join(b))

ART["n2_snow_s8"] = fig_s8()


# ---------------------------------------------------------------- S9: 반쪽에서 눈송이까지
def half_branch(cx, cy, R, rot, mirror=False, col=RED, w=4):
    """한가운데 (cx,cy)에서 rot(도, 0=위) 방향 줄기 반쪽 + 곁가지 둘(줄기와 60°, 길이 < 뿌리까지 거리)."""
    sg = -1 if mirror else 1
    segs = [((0, 0), (0, R))]
    for d, L in ((0.42 * R, 0.30 * R), (0.70 * R, 0.22 * R)):
        segs.append(((0, d), (sg * L * math.sin(math.radians(60)), d + L * math.cos(math.radians(60)))))
    a = math.radians(rot)
    def P(p):
        x, y = p   # y = 줄기 방향
        return cx + x * math.cos(a) + y * math.sin(a), cy + x * math.sin(a) - y * math.cos(a)
    out = []
    for p0, p1 in segs:
        (x0, y0), (x1, y1) = P(p0), P(p1)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def ray(cx, cy, R, rot, c=NAVY, w=1.4, dash="5 5", op=1):
    a = math.radians(rot)
    return f'<line x1="{cx}" y1="{cy}" x2="{cx + R * math.sin(a):.1f}" y2="{cy - R * math.cos(a):.1f}" stroke="{c}" stroke-width="{w}" stroke-dasharray="{dash}" opacity="{op}"/>'


def wedge(cx, cy, R, a0, a1, fill):
    p = lambda a: (cx + R * math.sin(math.radians(a)), cy - R * math.cos(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    return f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{R},{R} 0 0 1 {x1:.1f},{y1:.1f} Z" fill="{fill}"/>'


def fig_s9():
    W, H = 720, 420
    R = 120
    b = []
    cxs = [110, 330, 590]; cy = 220
    # ① 반쪽 1개: 30° 칸
    cx = cxs[0]
    b.append(wedge(cx, cy + 50, R + 20, 0, 30, "#F4E3DC"))
    b.append(ray(cx, cy + 50, R + 20, 0, GRAY, 1.2, "4 4") + ray(cx, cy + 50, R + 20, 30, GRAY, 1.2, "4 4"))
    b.append(half_branch(cx, cy + 50, R, 0, mirror=False))
    b.append(f'<circle cx="{cx}" cy="{cy + 50}" r="4" fill="{INK}"/>')
    b.append(f'<path d="M{cx},{cy + 50 - 34} A34,34 0 0 1 {cx + 34 * math.sin(math.radians(30)):.1f},{cy + 50 - 34 * math.cos(math.radians(30)):.1f}" stroke="{INK}" stroke-width="1.2" fill="none"/>')
    b.append(t(cx + 20, cy + 50 - 42, "30°", 18, INK))
    # ② 뒤집어 붙이면 가지 1개(60° 칸)
    cx = cxs[1]
    b.append(wedge(cx, cy + 50, R + 20, -30, 30, "#ECEFF3"))
    b.append(ray(cx, cy + 50, R + 20, -30, GRAY, 1.2, "4 4") + ray(cx, cy + 50, R + 20, 30, GRAY, 1.2, "4 4"))
    b.append(half_branch(cx, cy + 50, R, 0, mirror=False))
    b.append(half_branch(cx, cy + 50, R, 0, mirror=True, col=NAVY))
    b.append(ray(cx, cy + 50, R + 30, 0, NAVY, 2, "7 5"))
    b.append(f'<path d="M{cx + 30},{cy - 50} q-30,-26 -60,0" stroke="{NAVY}" stroke-width="2" fill="none" marker-end="url(#arrN)"/>')
    b.append(f'<circle cx="{cx}" cy="{cy + 50}" r="4" fill="{INK}"/>')
    b.append(t(cx + 26, cy + 50 - 52, "60°", 18, INK))
    b.append(f'<path d="M{cx + 46 * math.sin(math.radians(-30)):.1f},{cy + 50 - 46 * math.cos(math.radians(-30)):.1f} A46,46 0 0 1 {cx + 46 * math.sin(math.radians(30)):.1f},{cy + 50 - 46 * math.cos(math.radians(30)):.1f}" stroke="{INK}" stroke-width="1.2" fill="none"/>')
    # ③ 60°씩 돌려 6개 → 반쪽 12개
    cx = cxs[2]
    for k in range(12):
        b.append(ray(cx, cy, R + 12, 30 * k, NAVY, 1.1, "4 5", .6))
    for k in range(6):
        b.append(half_branch(cx, cy, R, 60 * k, mirror=False, w=3.4))
        b.append(half_branch(cx, cy, R, 60 * k, mirror=True, col=NAVY, w=3.4))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{INK}"/>')
    # 화살표·라벨
    b.append(line(178, 200, 238, 200, INK, 2, mk="arr"))
    b.append(line(420, 200, 450, 200, INK, 2, mk="arr"))
    b.append(t(cxs[0] + 10, H - 46, "반쪽 1개", 20, RED, "middle"))
    b.append(tl(cxs[1], H - 46, ["뒤집어 붙이면", "가지 1개(2조각)"], 20, INK, "middle", 700, 1.3))
    b.append(tl(cxs[2], H - 46, ["60°씩 돌려 6개", "→ 2×6=12조각"], 20, INK, "middle", 700, 1.3))
    return svg("n2_snow_s9", W, H, "".join(b))

ART["n2_snow_s9"] = fig_s9()


# ---------------------------------------------------------------- S10: 여섯 갈래 종이 눈송이 접는 순서
def scissors(x, y, s=1.0, rot=0):
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})" stroke="{RED}" stroke-width="2" fill="none">'
            f'<circle cx="-12" cy="-6" r="5"/><circle cx="-12" cy="6" r="5"/><line x1="-8" y1="-4" x2="14" y2="5"/><line x1="-8" y1="4" x2="14" y2="-5"/></g>')


def fig_s10():
    W, H = 720, 700
    PW, PH = 345, 300
    pos = [(10, 14), (365, 14), (10, 336), (365, 336)]
    b = []
    for i, (x, y) in enumerate(pos):
        b.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
        b.append(f'<circle cx="{x + 20}" cy="{y + 22}" r="14" fill="{INK}"/>' + t(x + 20, y + 29, "①②③④"[i], 19, PAPER, "middle"))
    k = 0.72   # A4 210×297 mm → 화면
    # ① 반으로 접기(위쪽 반을 아래로): 2겹
    x, y = pos[0]; w, h = 210 * k, 297 * k; x0, y0 = x + 70, y + 40
    b.append(f'<rect x="{x0}" y="{y0}" width="{w:.0f}" height="{h:.0f}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.8"/>')
    b.append(line(x0 - 8, y0 + h / 2, x0 + w + 8, y0 + h / 2, NAVY, 2.2, "8 6"))
    b.append(f'<path d="M{x0 + w + 18},{y0 + 24} C{x0 + w + 56},{y0 + 40} {x0 + w + 56},{y0 + h - 60} {x0 + w + 20},{y0 + h - 30}" stroke="{NAVY}" stroke-width="2.4" fill="none" marker-end="url(#arrN)"/>')
    b.append(t(x + 34, y + PH - 22, "2겹", 22, RED, "middle", 900))
    # ② 또 반으로 접기: 두 접힌 선이 만나는 곳 = 눈송이 한가운데
    x, y = pos[1]; w, h = 210 * k, 148.5 * k; x0, y0 = x + 60, y + 90
    b.append(f'<rect x="{x0 + 4}" y="{y0 + 4}" width="{w:.0f}" height="{h:.0f}" fill="#EDE7DA" stroke="{INK}" stroke-width="1"/>')
    b.append(f'<rect x="{x0}" y="{y0}" width="{w:.0f}" height="{h:.0f}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.8"/>')
    b.append(line(x0 + w / 2, y0 - 10, x0 + w / 2, y0 + h + 10, NAVY, 2.2, "8 6"))
    b.append(f'<path d="M{x0 + w - 10},{y0 + h + 24} C{x0 + w - 30},{y0 + h + 52} {x0 + w / 2 - 20},{y0 + h + 52} {x0 + w / 2 - 40},{y0 + h + 26}" stroke="{NAVY}" stroke-width="2.4" fill="none" marker-end="url(#arrN)"/>')
    b.append(f'<circle cx="{x0 + w / 2:.1f}" cy="{y0}" r="7" fill="{RED}"/>')
    b.append(line(x0 + w / 2 + 6, y0 - 6, x0 + w / 2 + 40, y0 - 36, RED, 1.4))
    b.append(t(x0 + w / 2 + 44, y0 - 40, "눈송이 한가운데", 18, RED))
    b.append(t(x0 - 4, y0 - 10, "접힌 선", 18, GRAY, "start", 500))
    b.append(t(x + 34, y + PH - 22, "4겹", 22, RED, "middle", 900))
    # ③ 꼭짓점의 직각을 30°씩 셋으로: 한쪽을 접어 올리고 나머지를 겹쳐 접기 → 12겹
    x, y = pos[2]; w, h = 148.5 * k * 1.25, 105 * k * 1.25
    ox, oy = x + 70, y + 250           # 빨강 점(한가운데) = 왼쪽 아래 꼭짓점, 직각
    b.append(f'<rect x="{ox}" y="{oy - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.8"/>')
    for ang in (30, 60):
        L = 180
        b.append(f'<line x1="{ox}" y1="{oy}" x2="{ox + L * math.cos(math.radians(ang)):.1f}" y2="{oy - L * math.sin(math.radians(ang)):.1f}" stroke="{NAVY}" stroke-width="2.2" stroke-dasharray="8 6"/>')
    for i, ang in enumerate((15, 45, 75)):
        b.append(t(ox + 62 * math.cos(math.radians(ang)) - 2, oy - 62 * math.sin(math.radians(ang)) + 7, "30°", 18, INK, "middle"))
    b.append(f'<path d="M{ox + w - 8:.1f},{oy - 12} C{ox + w + 34:.1f},{oy - 40} {ox + w + 20:.1f},{oy - 120} {ox + 150:.1f},{oy - 134}" stroke="{NAVY}" stroke-width="2.4" fill="none" marker-end="url(#arrN)"/>')
    b.append(t(ox + w + 30, oy - 16, "1", 20, NAVY, "middle", 900))
    b.append(f'<path d="M{ox + 12},{oy - h - 12:.1f} C{ox + 20},{oy - h - 70:.1f} {ox + 100},{oy - h - 70:.1f} {ox + 128},{oy - h - 26:.1f}" stroke="{NAVY}" stroke-width="2.4" fill="none" marker-end="url(#arrN)"/>')
    b.append(t(ox - 6, oy - h - 22, "2", 20, NAVY, "middle", 900))
    b.append(f'<circle cx="{ox}" cy="{oy}" r="7" fill="{RED}"/>')
    b.append(t(x + PW - 16, y + PH - 22, "4×3=12겹", 22, RED, "end", 900))
    # ④ 삐져나온 끝을 자르고 가장자리를 오려 냄 → 펼치면 여섯 갈래
    x, y = pos[3]
    ox, oy = x + 46, y + 262
    tip = 40
    L1, L2 = 230, 175               # 30° 쐐기, 반대쪽 끝이 길게 삐져나옴(A4라 길어요)
    a0, a1 = math.radians(52), math.radians(82)
    p0 = (ox + L1 * math.cos(a0), oy - L1 * math.sin(a0)); p1 = (ox + L1 * math.cos(a1), oy - L1 * math.sin(a1))
    b.append(f'<path d="M{ox},{oy} L{p0[0]:.1f},{p0[1]:.1f} L{p0[0] - 16:.1f},{p0[1] - 34:.1f} L{p1[0]:.1f},{p1[1]:.1f} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.8"/>')
    q0 = (ox + L2 * math.cos(a0), oy - L2 * math.sin(a0)); q1 = (ox + L2 * math.cos(a1), oy - L2 * math.sin(a1))
    b.append(f'<path d="M{q0[0]:.1f},{q0[1]:.1f} L{p0[0]:.1f},{p0[1]:.1f} L{p0[0] - 16:.1f},{p0[1] - 34:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{q1[0]:.1f},{q1[1]:.1f} Z" fill="url(#hatch)"/>')
    b.append(line(q0[0] + 8, q0[1] + 6, q1[0] - 8, q1[1] - 2, RED, 3))
    b.append(scissors(q0[0] + 26, q0[1] + 10, 1.0, 190))
    # 가장자리 오리는 자리(빨강 홈)
    for f in (0.35, 0.6):
        ax_, ay_ = ox + L2 * f * math.cos(a0), oy - L2 * f * math.sin(a0)
        b.append(f'<path d="M{ax_ - 6:.1f},{ay_ + 7:.1f} l14,-2 l-6,-12" stroke="{RED}" stroke-width="2.4" fill="none"/>')
        bx_, by_ = ox + L2 * f * math.cos(a1), oy - L2 * f * math.sin(a1)
        b.append(f'<path d="M{bx_ + 2:.1f},{by_ + 10:.1f} l-12,-4 l8,-12" stroke="{RED}" stroke-width="2.4" fill="none"/>')
    b.append(f'<circle cx="{ox}" cy="{oy}" r="6" fill="{RED}"/>')
    # 펼친 눈송이(여섯 갈래, 접힌 선 12줄)
    sx, sy, R = x + 262, y + 130, 62
    for kk in range(12): b.append(ray(sx, sy, R + 8, 30 * kk, NAVY, 1, "3 4", .7))
    for kk in range(6):
        b.append(half_branch(sx, sy, R, 60 * kk, False, INK, 3) + half_branch(sx, sy, R, 60 * kk, True, INK, 3))
    b.append(line(x + 160, y + 170, x + 190, y + 150, INK, 2, mk="arr"))
    b.append(t(sx, sy + R + 34, "펼치면", 18, INK, "middle"))
    b.append(t(sx, sy + R + 58, "여섯 갈래", 18, INK, "middle"))
    b.append(t(x + PW - 16, y + PH - 22, "자르고 오리기", 20, RED, "end", 900))
    b.append(t(W / 2, H - 22, "겹 수: 2 → 4 → 12", 22, INK, "middle", 900))
    return svg("n2_snow_s10", W, H, "".join(b))

ART["n2_snow_s10"] = fig_s10()


# ---------------------------------------------------------------- S11: 1,000원 바구니와 28칸 블록
def fig_s11():
    W, H = 720, 820
    b = []
    cs = 34; gx, gy = 40, 96             # 블록 7×4, 맨 윗줄부터 왼쪽→오른쪽으로 셈
    bx0, bx1, by0 = gx - 14, gx + 7 * cs + 14, gy + 4 * cs + 4
    b.append(f'<path d="M{bx0 + 40},{by0} Q{(bx0 + bx1) / 2},{by0 - 70} {bx1 - 40},{by0}" stroke="{INK}" stroke-width="3" fill="none"/>')
    for i in range(28):
        r_, c_ = divmod(i, 7)
        x = gx + c_ * cs; y = gy + r_ * cs
        f = RED if i < 5 else "url(#dotN)"
        b.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="{PAPER}"/><rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="{f}"/>')
        if i == 5: b.append(f'<rect x="{x}" y="{y}" width="{cs * 0.6:.1f}" height="{cs}" fill="{RED}"/>')
        b.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    b.append(t(gx, gy - 18, "올해 +28원", 24, INK, "start", 900))
    b.append(t(gx + 7 * cs + 18, gy + cs / 2 + 7, "← 그 가운데 기름 몫 5원 60전", 19, RED, "start", 900))
    b.append(f'<path d="M{bx0},{by0} L{bx1},{by0} L{bx1 - 18},{by0 + 74} L{bx0 + 18},{by0 + 74} Z" fill="#F3E6C4" stroke="{INK}" stroke-width="2"/>')
    b.append("".join(f'<line x1="{bx0 + 10 + k * 26}" y1="{by0 + 4}" x2="{bx0 + 22 + k * 24}" y2="{by0 + 70}" stroke="{INK}" stroke-width="1" opacity=".45"/>' for k in range(10)))
    b.append(tb((bx0 + bx1) / 2, by0 + 46, "작년 1,000원", 20, INK, "middle"))
    # 28칸을 한 줄로 펼쳐 5.6칸 묶음 다섯 개
    sx0, sy, u = 330, 230, 12
    b.append(t(sx0, sy - 14, "28칸을 한 줄로 펼치면", 18, GRAY, "start", 500))
    for i in range(28):
        f = RED if i < 5 else "url(#dotN)"
        b.append(f'<rect x="{sx0 + i * u}" y="{sy}" width="{u}" height="24" fill="{PAPER}"/><rect x="{sx0 + i * u}" y="{sy}" width="{u}" height="24" fill="{f}"/>')
        if i == 5: b.append(f'<rect x="{sx0 + i * u}" y="{sy}" width="{u * .6:.1f}" height="24" fill="{RED}"/>')
        b.append(f'<rect x="{sx0 + i * u}" y="{sy}" width="{u}" height="24" fill="none" stroke="{INK}" stroke-width=".8"/>')
    for g in range(5):
        a0, a1 = sx0 + g * 5.6 * u, sx0 + (g + 1) * 5.6 * u
        c = RED if g == 0 else NAVY
        b.append(f'<path d="M{a0 + 2:.1f},{sy + 30} q0,8 8,8 L{(a0 + a1) / 2 - 4:.1f},{sy + 38} l4,6 l4,-6 L{a1 - 10:.1f},{sy + 38} q8,0 8,-8" stroke="{c}" stroke-width="1.8" fill="none"/>')
    b.append(tl(sx0, sy + 76, ["5원 60전짜리 묶음이 다섯 개", "→ 다섯 몫 가운데 한 몫"], 19, INK, "start", 700, 1.35))
    # 1,000원당 오른 값(막대 길이 = 28 : 149 : 197 : 116)
    y0 = 400
    b.append(line(20, y0 - 20, W - 20, y0 - 20, INK, 1))
    b.append(t(40, y0 + 20, "1,000원당 오른 값", 22, INK, "start", 900))
    k = 3.0
    bars = [("바구니 전체", 28, NAVY), ("석유류", 149, RED), ("경유", 197, NAVY), ("휘발유", 116, NAVY)]
    for i, (nm, v, c) in enumerate(bars):
        y = y0 + 70 + i * 76
        b.append(t(40, y - 10, f"{nm}: 1,000원당 {v}원", 19, RED if c == RED else INK, "start", 700))
        fill = RED if c == RED else "url(#dotN)"
        b.append(f'<rect x="40" y="{y}" width="{v * k:.1f}" height="28" fill="{PAPER}" stroke="{c}" stroke-width="1.8"/><rect x="40" y="{y}" width="{v * k:.1f}" height="28" fill="{fill}"/>')
    b.append(t(W - 20, H - 18, "2026년 10월, 작년 10월과 견줌 (국가데이터처)", 18, GRAY, "end", 500))
    return svg("n2_economy_s11", W, H, "".join(b))

ART["n2_economy_s11"] = fig_s11()


# ---------------------------------------------------------------- S12: 1억에서 1조까지(1만 칸 모눈)
def fig_s12():
    W, H = 720, 780
    n, c = 100, 4.4; gx, gy = 30, 80           # 모눈 왼쪽 위
    G = n * c; bot = gy + G
    b = [t(W / 2, 44, "한 칸 = 1억 달러, 전체 = 1조 달러", 24, INK, "middle", 900)]
    # 왼쪽 아래부터 쌓인 줄 수: 1977 1줄(100칸), 1995 10줄(1,000칸), 2025 70줄(7,000칸), 2026 100줄(1만 칸)
    tones = [(100, "#C9D3E0"), (70, "#7D93AF"), (1, "#14263F")]   # 1995년 줄은 출처 확인 전이라 뺌(협의록)
    for rows, col in tones:
        b.append(f'<rect x="{gx}" y="{bot - rows * c:.1f}" width="{G:.1f}" height="{rows * c:.1f}" fill="{col}"/>')
    for i in range(0, n + 1, 10):
        b.append(line(gx + i * c, gy, gx + i * c, bot, PAPER, .8))
        b.append(line(gx, gy + i * c, gx + G, gy + i * c, PAPER, .8))
    b.append(f'<rect x="{gx}" y="{bot - c:.1f}" width="{c}" height="{c}" fill="{RED}"/>')
    b.append(f'<rect x="{gx}" y="{gy}" width="{G:.1f}" height="{G:.1f}" fill="none" stroke="{RED}" stroke-width="3"/>')
    # 오른쪽 괄호(누적): 안쪽이 먼저, 바깥이 나중
    def brace(x, rows, lab, col, ly, lx):
        y0 = bot - rows * c
        out = f'<path d="M{x - 6},{y0 + 1:.1f} L{x},{y0 + 1:.1f} L{x},{bot - 1:.1f} L{x - 6},{bot - 1:.1f}" stroke="{col}" stroke-width="2" fill="none"/>'
        out += line(x, y0 + 1, lx - 6, ly - 6, col, 1.2)
        out += tl(lx, ly, lab, 18, col, "start", 700, 1.27)
        return out
    xr = gx + G
    lx = xr + 70
    b.append(brace(xr + 58, 100, ["2026년 11월 19일", "1조 달러", "= 1만 칸"], RED, gy + 16, lx))
    b.append(brace(xr + 44, 70, ["2025년", "7,000억 달러", "= 7,000칸"], NAVY, bot - 70 * c + 16, lx))
    b.append(brace(xr + 16, 1, ["1977년", "100억 달러", "= 100칸(한 줄)"], NAVY, bot + 32, lx))
    # 돋보기: 1964년 1칸
    mx, my, mr = 150, bot + 140, 82
    zc = 26
    b.append(line(gx + c / 2, bot - c / 2, mx - 50, my - 64, INK, 1.4))
    b.append(f'<circle cx="{gx + c / 2:.1f}" cy="{bot - c / 2:.1f}" r="7" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<clipPath id="zc"><circle cx="{mx}" cy="{my}" r="{mr}"/></clipPath>')
    zx0, zy0 = mx - 2 * zc - 6, my + 2 * zc + 6      # 확대한 모눈의 왼쪽 아래 모서리
    zoom = [f'<rect x="{mx - mr}" y="{my - mr}" width="{2 * mr}" height="{2 * mr}" fill="#C9D3E0"/>',
            f'<rect x="{zx0}" y="{my - mr}" width="{2 * mr}" height="{zy0 - my + mr}" fill="#7D93AF"/>',
            f'<rect x="{zx0}" y="{zy0 - zc}" width="{2 * mr}" height="{zc}" fill="#14263F"/>',
            f'<rect x="{zx0 - 2 * mr}" y="{my - mr}" width="{2 * mr}" height="{2 * mr}" fill="{PAPER}"/>',
            f'<rect x="{mx - mr}" y="{zy0}" width="{2 * mr}" height="{mr}" fill="{PAPER}"/>']
    for i in range(-1, 8):
        zoom.append(line(zx0 + i * zc, my - mr, zx0 + i * zc, zy0, PAPER, 1.2))
        zoom.append(line(zx0, zy0 - i * zc, mx + mr, zy0 - i * zc, PAPER, 1.2))
    zoom.append(f'<rect x="{zx0}" y="{zy0 - zc}" width="{zc}" height="{zc}" fill="{RED}" stroke="{PAPER}" stroke-width="1.2"/>')
    zoom.append(f'<path d="M{zx0},{my - mr} L{zx0},{zy0} L{mx + mr},{zy0}" stroke="{RED}" stroke-width="3" fill="none"/>')
    b.append(f'<g clip-path="url(#zc)">{"".join(zoom)}</g><circle cx="{mx}" cy="{my}" r="{mr}" fill="none" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<line x1="{mx + mr * .72:.0f}" y1="{my + mr * .72:.0f}" x2="{mx + mr * .72 + 22:.0f}" y2="{my + mr * .72 + 22:.0f}" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>')
    b.append(tl(mx + mr + 34, my - 10, ["1964년 1억 달러", "= 1칸"], 20, RED, "start", 900, 1.3))
    b.append(t(mx + mr + 34, my + 48, "(크게 보기)", 18, GRAY, "start", 500))
    b.append(tl(W - 20, H - 52, ["62년 동안 1칸이 1만 칸이 됐어요.", "(관계부처 합동 자료)"], 18, GRAY, "end", 500, 1.35))
    return svg("n2_export_s12", W, H, "".join(b))

ART["n2_export_s12"] = fig_s12()


# ---------------------------------------------------------------- S13: 100달러 가운데 49달러
def fig_s13():
    W, H = 720, 520
    c, gx, gy = 36, 40, 74          # 10×10, 아래부터 채움
    b = [t(gx, 44, "10월 수출을 100달러로 줄이면", 24, INK, "start", 900)]
    for i in range(100):
        r_, c_ = divmod(i, 10)
        x = gx + c_ * c; y = gy + (9 - r_) * c
        f = RED if i < 49 else "url(#dotN)"
        b.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="{PAPER}"/><rect x="{x + 1}" y="{y + 1}" width="{c - 2}" height="{c - 2}" fill="{f}"/>')
        b.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="none" stroke="{INK}" stroke-width="1"/>')
    gr = gx + 10 * c
    b.append(f'<path d="M{gr + 10},{gy + 10 * c} L{gr + 18},{gy + 10 * c} L{gr + 18},{gy + 5 * c + 2} L{gr + 10},{gy + 5 * c + 2}" stroke="{RED}" stroke-width="2" fill="none"/>')
    b.append(tl(gr + 30, gy + 7.2 * c - 4, ["반도체", "약 49달러"], 22, RED, "start", 900, 1.3))
    b.append(tl(gr + 30, gy + 7.5 * c + 56, ["빨간 칸 49개:", "다섯 줄에서 한 칸 모자라요"], 18, RED, "start", 500, 1.3))
    b.append(f'<path d="M{gr + 10},{gy + 5 * c - 2} L{gr + 18},{gy + 5 * c - 2} L{gr + 18},{gy} L{gr + 10},{gy}" stroke="{NAVY}" stroke-width="2" fill="none"/>')
    b.append(tl(gr + 30, gy + 1.8 * c, ["자동차, 석유제품,", "컴퓨터 등", "약 51달러"], 20, NAVY, "start", 700, 1.3))
    b.append(t(W - 14, H - 18, "2026년 10월 (산업통상부)", 18, GRAY, "end", 500))
    return svg("n2_export_s13", W, H, "".join(b))

ART["n2_export_s13"] = fig_s13()


# ---------------------------------------------------------------- S14: 소리 모양 두 줄 + 맞힌 횟수
def fig_s14():
    W, H = 720, 470
    b = []
    # 왼쪽: 소리 모양(설명용)
    b.append(t(20, 40, "소리 모양", 20, GRAY, "start", 700))
    y1, y2 = 120, 250
    b.append(t(20, y1 + 8, "야옹", 22, RED, "start", 900))
    r = random.Random(4)
    for k, (x0, L, A) in enumerate([(92, 50, 30), (164, 34, 22), (218, 62, 36)]):
        pts = []
        n = int(L / 4)
        for i in range(n + 1):
            env = math.sin(math.pi * i / n)
            amp = A * env * r.uniform(.4, 1.0)
            pts.append(f"{x0 + i * L / n:.1f},{y1 + (amp if i % 2 else -amp):.1f}")
        b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linejoin="round"/>')
    b.append(line(90, y1, 300, y1, "#D9D3C6", 1))
    b.append(t(20, y2 + 8, "가르랑", 22, NAVY, "start", 900))
    pts = " ".join(f"{100 + i * 2:.1f},{y2 + 12 * math.sin(i * 1.15):.1f}" for i in range(101))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{NAVY}" stroke-width="2"/>')
    b.append(tl(20, 340, ["설명용 그림이에요", "(실제 측정 그래프가 아니에요)"], 18, GRAY, "start", 500, 1.3))
    b.append(line(326, 30, 326, 400, INK, 1))
    # 오른쪽: 맞힌 횟수(동그라미)
    x0 = 352; rr = 12; gap = 33
    b.append(t(x0, 40, "컴퓨터가 맞힌 횟수", 20, GRAY, "start", 700))
    def row(y, n, full, col, half=False):
        out = []
        for i in range(n):
            cx = x0 + rr + i * gap
            out.append(f'<circle cx="{cx}" cy="{y}" r="{rr}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
            if i < full: out.append(f'<circle cx="{cx}" cy="{y}" r="{rr - 1}" fill="{col}"/>')
            if half and i == full: out.append(f'<path d="M{cx},{y - rr + 1} A{rr - 1},{rr - 1} 0 0 0 {cx},{y + rr - 1} Z" fill="{col}"/>')
        return "".join(out)
    b.append(t(x0, 96, "가르랑: 10번 중 8번 넘게", 20, NAVY, "start", 900))
    b.append(row(124, 10, 8, NAVY, half=True))
    b.append(t(x0, 190, "야옹: 10번 중 6번쯤", 20, RED, "start", 900))
    b.append(row(218, 10, 6, RED))
    b.append(t(x0, 284, "아무나 찍으면: 8번에 1번쯤", 20, GRAY, "start", 900))
    b.append(row(312, 8, 1, GRAY))
    b.append(t(W / 2, H - 24, "같은 고양이 8마리의 소리로 컴퓨터가 맞힌 결과예요.", 18, GRAY, "middle", 500))
    return svg("n2_purr_s14", W, H, "".join(b))

ART["n2_purr_s14"] = fig_s14()


# ---------------------------------------------------------------- S15: 네 자리 그림 기호(같은 크기·굵기, 글자 없음)
ICON = {
    # 든든한 받침: 두 손으로 의자 다리를 꼭 잡은 모습
    "a": ('<path d="M40,6 L40,34 M14,34 L44,34 M17,34 L17,60 M40,34 L40,60"/>'
          '<rect x="9" y="41" width="16" height="12" rx="5" fill="#F4DCD2"/><rect x="32" y="41" width="16" height="12" rx="5" fill="#F4DCD2"/>'
          '<path d="M13,53 q4,-5 8,0 M36,53 q4,-5 8,0" stroke-width="1.6"/>'),
    # 손 뻗는 등반가: 위로 쭉 뻗은 팔과 펼친 손
    "b": ('<path d="M26,62 L28,32 M38,62 L36,32"/>'
          '<path d="M27,16 L26,5 M31,15 L31,3 M35,15 L36,4 M38,18 L42,9 M25,25 L18,19"/>'
          '<ellipse cx="32" cy="24" rx="8" ry="9" fill="#F4DCD2"/>'),
    # 길 찾는 눈: 돋보기
    "c": ('<circle cx="26" cy="26" r="15" fill="#E3E8EE"/><path d="M37,37 L54,54" stroke-width="6"/>'),
    # 힘 주는 응원: 작은 깃발
    "d": ('<path d="M18,58 L18,8"/><path d="M18,10 L50,18 L18,30 Z" fill="#F4DCD2"/>'),
}


def icon(key, x=0, y=0, size=64, col=INK):
    k = size / 64
    return (f'<g transform="translate({x},{y}) scale({k:.3f})" fill="none" stroke="{col}" stroke-width="3.2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[key]}</g>')


def fig_s15():
    b = "".join(icon(k, 8 + i * 80, 8) for i, k in enumerate("abcd"))
    return svg("n2_psy_s15", 320, 80, b)

ART["n2_psy_s15"] = fig_s15()
for _k in "abcd":
    ART[f"n2_psy_s15_{_k}"] = svg(f"n2_psy_s15_{_k}", 64, 64, icon(_k), bg="none")

# ==== 저장
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, v in ART.items():
        open(os.path.join(OUT, k + ".svg"), "w", encoding="utf-8").write(v)
    print(len(ART), "개 저장:", ", ".join(ART))
