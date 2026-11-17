# 서아 페이퍼 제1호 도판(레트로 선화: 잉크 + 빨강/남색 + 망점)
import math
INK, RED, NAVY, PAPER, GRAY = "#1C1A17", "#C8372D", "#1F3A5F", "#FBF8F1", "#6B655C"
SANS = "Noto Sans KR, sans-serif"
DEFS = f'''<defs>
<pattern id="dot" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="{INK}" opacity=".55"/></pattern>
<pattern id="dotR" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.3" fill="{RED}" opacity=".7"/></pattern>
<pattern id="dotN" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.2" fill="{NAVY}" opacity=".6"/></pattern>
<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="{INK}" stroke-width="1.2" opacity=".5"/></pattern>
<marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{INK}"/></marker>
<marker id="arrR" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{RED}"/></marker>
<marker id="arrN" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="{NAVY}"/></marker>
</defs>'''

def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">{DEFS}<rect width="{w}" height="{h}" fill="{PAPER}"/>{body}</svg>'

def t(x, y, s, size=15, color=INK, anchor="start", weight=700):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'

def tb(x, y, s, size=14, color=INK, anchor="start", weight=700):
    w = len(s) * size * 0.98 + 10; h = size + 8
    x0 = x - 5 if anchor == "start" else (x - w/2 if anchor == "middle" else x - w + 5)
    return f'<rect x="{x0:.0f}" y="{y-size-2:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{PAPER}" stroke="{color}" stroke-width="1"/>' + t(x, y, s, size, color, anchor, weight)

def stars(w, h, n, seed=1, color="#F4EFE4"):
    out = []
    for i in range(n):
        x = (i * 97 + seed * 31) % w; y = (i * 57 + seed * 13) % h; r = 0.8 + (i * 7 % 3) * 0.6
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    return "".join(out)

def voyager_craft(x, y, s=1.0, stroke="#F4EFE4"):
    return f'''<g transform="translate({x},{y}) scale({s})" stroke="{stroke}" stroke-width="2.4" fill="none" stroke-linecap="round">
<path d="M-70 -10 Q0 -60 70 -10 Z" fill="{PAPER}" stroke="{stroke}"/><path d="M-70 -10 Q0 -60 70 -10" />
<line x1="0" y1="-36" x2="0" y2="-12"/><line x1="-30" y1="-12" x2="0" y2="-36"/><line x1="30" y1="-12" x2="0" y2="-36"/>
<rect x="-18" y="-10" width="36" height="22" fill="{NAVY}"/>
<line x1="-18" y1="2" x2="-120" y2="40"/><rect x="-140" y="36" width="24" height="12" fill="{RED}" stroke="{stroke}"/>
<line x1="18" y1="4" x2="150" y2="-6"/><circle cx="150" cy="-6" r="5" fill="{stroke}"/>
<line x1="6" y1="12" x2="40" y2="70"/><rect x="34" y="68" width="16" height="10"/>
<line x1="-6" y1="12" x2="-30" y2="110"/>
</g>'''

ART = {}

# 표지: 보이저 1호와 창백한 푸른 점
ART["cover"] = svg(800, 560, f'''
<rect x="0" y="0" width="800" height="560" fill="{NAVY}"/>
<rect x="0" y="0" width="800" height="560" fill="url(#dot)" opacity=".35"/>
{stars(800, 560, 120, 3)}
<circle cx="120" cy="430" r="5" fill="#8FC3FF"/><circle cx="120" cy="430" r="16" fill="none" stroke="#F4EFE4" stroke-width="1.5" stroke-dasharray="3 4"/>
{t(142, 470, "지구", 18, "#F4EFE4")}
<path d="M140 418 Q 420 300 560 210" stroke="{RED}" stroke-width="3" fill="none" stroke-dasharray="10 8" marker-end="url(#arrR)"/>
{t(300, 330, "빛으로 24시간", 22, "#F4EFE4")}
{voyager_craft(600, 170, 1.15)}
{t(600, 330, "보이저 1호", 22, "#F4EFE4", "middle")}
{t(600, 356, "1977년 발사 · 약 259억 km", 15, "#F4EFE4", "middle", 500)}
<rect x="18" y="18" width="200" height="34" fill="{RED}"/>{t(118, 41, "2026. 11. 18 저녁", 17, "#fff", "middle")}
''')

# 보이저 기사: 1광일 거리와 통신 시간
ART["voyager"] = svg(800, 360, f'''
{t(30, 40, "1광일 = 빛이 24시간 동안 가는 거리 ≈ 259억 km", 19)}
<circle cx="80" cy="180" r="26" fill="url(#dotN)" stroke="{INK}" stroke-width="2"/>{t(80, 236, "지구", 16, INK, "middle")}
<g transform="translate(700,180) scale(.45)">{voyager_craft(0, 0, 1, INK)}</g>{t(700, 250, "보이저 1호", 16, INK, "middle")}
<line x1="112" y1="160" x2="640" y2="160" stroke="{RED}" stroke-width="3" marker-end="url(#arrR)"/>
{t(376, 150, "명령 보내기: 24시간", 16, RED, "middle")}
<line x1="640" y1="205" x2="112" y2="205" stroke="{NAVY}" stroke-width="3" marker-end="url(#arrN)"/>
{t(376, 232, "답 받기: 24시간", 16, NAVY, "middle")}
<line x1="30" y1="280" x2="770" y2="280" stroke="{INK}" stroke-width="1"/>
{t(30, 310, "견주어 보기", 14, GRAY)}
{t(30, 336, "달 → 지구: 약 1.3초", 15, INK, "start", 500)}{t(260, 336, "태양 → 지구: 약 8분 19초", 15, INK, "start", 500)}{t(530, 336, "보이저 1호 → 지구: 약 24시간", 15, RED, "start", 700)}
''')

# 사자자리 유성우: 동쪽 하늘 복사점
leo = [(470,150),(445,128),(450,100),(478,86),(505,95),(470,150),(520,175),(590,190),(560,150),(520,175)]
ART["leonid"] = svg(800, 420, f'''
<rect width="800" height="420" fill="{INK}"/>{stars(800, 340, 90, 7)}
<path d="M0 340 Q 200 320 400 335 T 800 330 L800 420 L0 420 Z" fill="#2B2722"/>
{t(400, 395, "동쪽", 18, "#F4EFE4", "middle")}
<polyline points="{' '.join(f'{x},{y}' for x,y in leo)}" fill="none" stroke="#F4EFE4" stroke-width="1.2" opacity=".7"/>
{''.join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#F4EFE4"/>' for x,y in leo)}
<circle cx="470" cy="120" r="9" fill="none" stroke="{RED}" stroke-width="2.5"/>
{t(486, 70, "복사점(사자자리)", 16, "#F4EFE4")}
{''.join(f'<line x1="{470+math.cos(a)*40:.0f}" y1="{120+math.sin(a)*40:.0f}" x2="{470+math.cos(a)*(150+i*25):.0f}" y2="{120+math.sin(a)*(150+i*25):.0f}" stroke="{RED}" stroke-width="2.4" stroke-linecap="round"/>' for i,a in enumerate([math.pi*0.85, math.pi*1.1, math.pi*0.15, math.pi*0.45, math.pi*1.35, math.pi*0.65]))}
{t(30, 40, "유성은 하늘 어디에나 떨어지지만, 꼬리를 거꾸로 이으면 사자자리 쪽으로 모여요", 15, "#F4EFE4", "start", 500)}
''')

# 아이스큐브 단면
ART["icecube"] = svg(800, 500, f'''
<rect x="0" y="40" width="800" height="460" fill="#E9F0F4"/>
<rect x="0" y="40" width="800" height="460" fill="url(#dotN)" opacity=".18"/>
<line x1="0" y1="40" x2="800" y2="40" stroke="{INK}" stroke-width="2"/>
<rect x="340" y="10" width="120" height="30" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>{t(400, 31, "아이스큐브 연구동", 13, INK, "middle")}
{t(20, 30, "남극 얼음 표면", 14)}
{''.join(f'<line x1="{200+i*50}" y1="40" x2="{200+i*50}" y2="440" stroke="{INK}" stroke-width="1.4"/>' + ''.join(f'<circle cx="{200+i*50}" cy="{262+j*28}" r="5" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>' for j in range(7)) for i in range(9))}
<rect x="170" y="240" width="460" height="205" fill="none" stroke="{NAVY}" stroke-width="2" stroke-dasharray="8 6"/>
{tb(185, 120, "센서를 단 줄을 깊은 얼음 속에 내림", 14, INK)}
{tb(185, 228, "약 1세제곱킬로미터의 얼음", 14, NAVY)}
<line x1="760" y1="40" x2="760" y2="440" stroke="{INK}" stroke-width="1.2" marker-end="url(#arr)"/>{tb(752, 470, "깊이 수 km", 13, INK, "end")}
<line x1="520" y1="500" x2="425" y2="330" stroke="{RED}" stroke-width="3" stroke-dasharray="9 6" marker-end="url(#arrR)"/>
<path d="M425 330 L380 410 L470 410 Z" fill="#7FB7E8" opacity=".6"/>
<circle cx="425" cy="330" r="7" fill="{RED}"/>
{tb(20, 470, "① 땅 밑에서 올라온 중성미자", 14, RED)}
{tb(20, 492, "② 얼음과 부딪힌 자리에서 푸른 빛 → 센서가 감지", 14, NAVY)}
''')

# 까마귀 실험 시간표
ART["crow"] = svg(800, 360, f'''
<rect x="40" y="40" width="250" height="170" fill="#fff" stroke="{INK}" stroke-width="2"/>
{''.join(f'<circle cx="{70+(i*53)%200}" cy="{65+(i*37)%120}" r="5" fill="{INK}"/><line x1="{70+(i*53)%200}" y1="{65+(i*37)%120}" x2="{84+(i*53)%200}" y2="{65+(i*37)%120}" stroke="{RED}" stroke-width="2" marker-end="url(#arrR)"/>' for i in range(12))}
{t(165, 232, "화면: 점 대부분이 한쪽으로 움직임", 13, GRAY, "middle", 500)}
<g transform="translate(400,150)"><ellipse cx="0" cy="20" rx="44" ry="34" fill="{INK}"/><circle cx="-36" cy="-14" r="24" fill="{INK}"/><path d="M-58 -18 L-90 -10 L-58 -4 Z" fill="{INK}"/><circle cx="-40" cy="-18" r="4" fill="{PAPER}"/><path d="M30 10 L80 0 L60 30 Z" fill="{INK}"/><line x1="-10" y1="54" x2="-10" y2="76" stroke="{INK}" stroke-width="3"/><line x1="10" y1="54" x2="10" y2="76" stroke="{INK}" stroke-width="3"/></g>
{t(400, 245, "송장까마귀", 14, INK, "middle")}
<line x1="40" y1="300" x2="760" y2="300" stroke="{INK}" stroke-width="2.5"/>
{''.join(f'<line x1="{x}" y1="290" x2="{x}" y2="310" stroke="{c}" stroke-width="3"/>' + t(x, 335, lab, 14, c, "middle") + t(x, 282, ms, 15, c, "middle") for x, ms, lab, c in [(60, "0", "점이 나타남", INK), (260, "70밀리초", "뇌 신경세포가 방향을 구분", NAVY), (680, "235밀리초", "부리로 답(평균)", RED)])}
''')

# 공룡 뼈 단면과 적혈구
ART["dino"] = svg(800, 380, f'''
<ellipse cx="230" cy="200" rx="170" ry="140" fill="url(#hatch)" stroke="{INK}" stroke-width="2.5"/>
<ellipse cx="230" cy="200" rx="60" ry="48" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
{''.join(f'<circle cx="{230+math.cos(a)*r:.0f}" cy="{200+math.sin(a)*r*0.8:.0f}" r="7" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>' for a, r in [(i*0.7, 95 + (i%3)*18) for i in range(9)])}
<circle cx="318" cy="150" r="12" fill="none" stroke="{RED}" stroke-width="3"/>
<line x1="330" y1="146" x2="520" y2="90" stroke="{RED}" stroke-width="2"/><line x1="326" y1="160" x2="520" y2="300" stroke="{RED}" stroke-width="2"/>
<circle cx="620" cy="195" r="130" fill="#fff" stroke="{RED}" stroke-width="3"/>
<path d="M520 140 Q 620 180 720 140 L720 250 Q 620 210 520 250 Z" fill="#EEE3CF" stroke="{INK}" stroke-width="1.5"/>
{''.join(f'<ellipse cx="{545+i*30}" cy="{190+(i%2)*14}" rx="11" ry="7" fill="{RED}" stroke="{INK}" stroke-width="1.2"/>' for i in range(6))}
{t(230, 362, "공룡 팔다리뼈 단면(그림은 모식도)", 14, GRAY, "middle", 500)}
{t(620, 350, "혈관 통로 속 광물화된 적혈구", 15, RED, "middle")}
{t(230, 206, "골수강", 13, INK, "middle", 500)}
''')

# 다시마숲 조사 지역
ART["kelp"] = svg(800, 380, f'''
<rect width="800" height="380" fill="#E9F0F4"/><rect width="800" height="380" fill="url(#dotN)" opacity=".15"/>
<path d="M0 0 L300 0 Q 330 80 300 150 Q 260 230 310 300 Q 340 350 300 380 L0 380 Z" fill="#E4D9C3" stroke="{INK}" stroke-width="2"/>
{t(80, 60, "육지(캘리포니아 해안)", 14)}
{''.join(f'<circle cx="{x}" cy="{y}" r="11" fill="{f}" stroke="{INK}" stroke-width="2"/>' for x,y,f in [(380,70,RED),(360,170,RED),(410,240,NAVY),(370,320,NAVY),(470,110,PAPER),(480,290,PAPER)])}
<rect x="560" y="60" width="210" height="130" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
<circle cx="582" cy="88" r="9" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>{t(600, 93, "줄어든 숲 2곳", 14)}
<circle cx="582" cy="122" r="9" fill="{NAVY}" stroke="{INK}" stroke-width="1.5"/>{t(600, 127, "다시 자란 숲 2곳", 14)}
<circle cx="582" cy="156" r="9" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>{t(600, 161, "그대로인 숲 2곳", 14)}
<g transform="translate(640,280)"><rect x="-40" y="-20" width="80" height="40" fill="#F2C94C" stroke="{INK}" stroke-width="2"/><circle cx="28" cy="0" r="9" fill="#fff" stroke="{INK}" stroke-width="2"/><line x1="0" y1="-20" x2="0" y2="-70" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 4"/></g>
{t(640, 335, "원격 조종 잠수로봇(빌림)", 14, INK, "middle")}
{t(560, 40, "위성 자료로 고른 6곳", 15, RED)}
''')

# 카케야: 원과 세 꼭짓점 곡선
def deltoid(cx, cy, r):
    pts = []
    for k in range(121):
        a = 2*math.pi*k/120
        pts.append(f"{cx + r*(2*math.cos(a)+math.cos(2*a))/3:.1f},{cy + r*(2*math.sin(a)-math.sin(2*a))/3:.1f}")
    return "M" + " L".join(pts) + " Z"
ART["kakeya"] = svg(800, 400, f'''
<circle cx="200" cy="200" r="130" fill="url(#dotN)" fill-opacity=".5" stroke="{INK}" stroke-width="2.5"/>
<line x1="70" y1="200" x2="330" y2="200" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>
<line x1="108" y1="108" x2="292" y2="292" stroke="{RED}" stroke-width="2" opacity=".5"/><line x1="200" y1="70" x2="200" y2="330" stroke="{RED}" stroke-width="2" opacity=".5"/>
<circle cx="200" cy="200" r="5" fill="{INK}"/>
{t(200, 372, "가운데를 잡고 돌리면: 원", 16, INK, "middle")}
<path d="{deltoid(580, 205, 195)}" fill="url(#dotR)" fill-opacity=".6" stroke="{INK}" stroke-width="2.5"/>
<line x1="516" y1="205" x2="676" y2="205" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/>
<line x1="516" y1="205" x2="676" y2="205" stroke="{NAVY}" stroke-width="2" opacity=".5" transform="rotate(60 596 205)"/>
<line x1="516" y1="205" x2="676" y2="205" stroke="{NAVY}" stroke-width="2" opacity=".5" transform="rotate(120 596 205)"/>
{t(580, 372, "밀면서 돌리면: 세 꼭짓점 곡선(원의 절반 넓이)", 16, INK, "middle")}
{t(30, 36, "같은 길이의 바늘을 한 바퀴 돌리는 두 방법", 17, INK)}
''')

# 귀여움: 아기 도식 비율
def face(cx, cy, baby):
    if baby:
        return f'''<ellipse cx="{cx}" cy="{cy}" rx="95" ry="88" fill="#fff" stroke="{INK}" stroke-width="2.5"/>
<ellipse cx="{cx-34}" cy="{cy+18}" rx="15" ry="18" fill="{INK}"/><ellipse cx="{cx+34}" cy="{cy+18}" rx="15" ry="18" fill="{INK}"/>
<ellipse cx="{cx-60}" cy="{cy+46}" rx="14" ry="8" fill="url(#dotR)"/><ellipse cx="{cx+60}" cy="{cy+46}" rx="14" ry="8" fill="url(#dotR)"/>
<path d="M{cx-8} {cy+52} q8 7 16 0" stroke="{INK}" stroke-width="2.5" fill="none"/>
<line x1="{cx-120}" y1="{cy+18}" x2="{cx+120}" y2="{cy+18}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="6 5"/>'''
    return f'''<ellipse cx="{cx}" cy="{cy}" rx="62" ry="98" fill="#fff" stroke="{INK}" stroke-width="2.5"/>
<ellipse cx="{cx-24}" cy="{cy-20}" rx="9" ry="5" fill="{INK}"/><ellipse cx="{cx+24}" cy="{cy-20}" rx="9" ry="5" fill="{INK}"/>
<path d="M{cx} {cy-10} v34" stroke="{INK}" stroke-width="2"/><path d="M{cx-14} {cy+48} h28" stroke="{INK}" stroke-width="2.5"/>
<line x1="{cx-90}" y1="{cy-20}" x2="{cx+90}" y2="{cy-20}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="6 5"/>'''
ART["cute"] = svg(800, 380, f'''
{face(210, 180, False)}{face(570, 185, True)}
{t(210, 340, "어른 얼굴: 눈이 얼굴 가운데보다 위", 15, INK, "middle")}
{t(570, 340, "아기 도식: 큰 머리, 낮고 큰 눈, 동그란 볼", 15, INK, "middle")}
{t(400, 36, "빨간 점선 = 눈의 높이", 14, RED, "middle")}
''')

# 경제: 경기 순환과 한국은행 기준금리
ART["economy"] = svg(800, 420, f'''
{t(30, 36, "경기는 오르내려요", 17)}
<line x1="40" y1="200" x2="420" y2="200" stroke="{INK}" stroke-width="1.5"/>
<path d="M40 170 C 90 70, 140 70, 190 170 S 290 270, 340 170 S 400 100, 420 120" stroke="{INK}" stroke-width="3" fill="none"/>
<circle cx="115" cy="95" r="6" fill="{RED}"/>{t(115, 80, "호황", 15, RED, "middle")}
<circle cx="265" cy="245" r="6" fill="{NAVY}"/>{t(265, 275, "불황", 15, NAVY, "middle")}
<line x1="115" y1="110" x2="115" y2="150" stroke="{RED}" stroke-width="2" marker-end="url(#arrR)"/>{t(125, 140, "금리↑로 식히기", 13, RED)}
<line x1="265" y1="230" x2="265" y2="195" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrN)"/>{t(275, 215, "금리↓로 띄우기", 13, NAVY)}
<line x1="460" y1="20" x2="460" y2="400" stroke="{INK}" stroke-width="1"/>
{t(490, 36, "한국은행 기준금리", 17)}
<line x1="500" y1="340" x2="780" y2="340" stroke="{INK}" stroke-width="1.5"/><line x1="500" y1="80" x2="500" y2="340" stroke="{INK}" stroke-width="1.5"/>
{''.join(t(492, 340 - (v-2.25)*320, f"{v:.2f}", 12, GRAY, "end", 500) + f'<line x1="500" y1="{340-(v-2.25)*320:.0f}" x2="780" y2="{340-(v-2.25)*320:.0f}" stroke="#CFC7B6" stroke-width="1"/>' for v in [2.50, 2.75, 3.00])}
<polyline points="500,{340-(2.5-2.25)*320:.0f} 620,{340-(2.5-2.25)*320:.0f} 620,{340-(2.75-2.25)*320:.0f} 690,{340-(2.75-2.25)*320:.0f} 690,{340-(3.0-2.25)*320:.0f} 780,{340-(3.0-2.25)*320:.0f}" fill="none" stroke="{RED}" stroke-width="3.5"/>
{t(620, 365, "2026.7.16", 12, INK, "middle", 500)}{t(690, 385, "2026.8.27", 12, INK, "middle", 500)}
{t(735, round(340-(3.0-2.25)*320-10), "3.00%", 15, RED, "middle")}
{t(560, 410, "단위: 연 %, 출처: 한국은행", 12, GRAY, "middle", 500)}
''')

# 예술: 마티에르(질감)와 빛
ART["art"] = svg(800, 380, f'''
{t(30, 36, "물감을 여러 겹 쌓은 화면의 단면(모식도)", 17)}
<rect x="60" y="250" width="680" height="34" fill="url(#hatch)" stroke="{INK}" stroke-width="2"/>{t(400, 306, "캔버스·화판", 13, INK, "middle", 500)}
<path d="M60 250 L60 200 Q 120 180 170 205 T 290 195 T 410 210 T 530 190 T 650 205 T 740 195 L740 250 Z" fill="#E8DCC4" stroke="{INK}" stroke-width="2"/>
<path d="M60 200 L60 170 Q 110 150 150 172 Q 180 140 230 168 Q 270 150 300 175 Q 350 140 390 170 Q 430 150 470 172 Q 520 140 560 168 Q 610 150 650 170 Q 700 145 740 168 L740 195 Q 650 205 530 190 Q 410 210 290 195 Q 170 205 60 200 Z" fill="url(#dot)" stroke="{INK}" stroke-width="2"/>
{''.join(f'<line x1="{x}" y1="60" x2="{x+30}" y2="{y}" stroke="{RED}" stroke-width="2" marker-end="url(#arrR)"/><line x1="{x+30}" y1="{y}" x2="{x+30+dx}" y2="{y-70}" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrN)"/>' for x,y,dx in [(120,165,-40),(260,160,45),(400,162,-10),(540,160,50),(660,163,-45)])}
{t(70, 75, "들어오는 빛", 14, RED)}{t(560, 75, "여러 방향으로 흩어지는 빛", 14, NAVY)}
{t(400, 350, "울퉁불퉁한 표면은 빛을 여러 방향으로 흩어, 보는 각도에 따라 느낌이 달라져요", 14, GRAY, "middle", 500)}
''')

# 마스코트(선화)와 선생님 아이콘(선화)
ART["mascot"] = f'''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
<path d="M52 78 L40 16 L88 58"/><path d="M148 78 L160 16 L112 58"/><path d="M86 46 L92 22 L100 42 L108 18 L114 46"/>
<ellipse cx="100" cy="112" rx="70" ry="62" fill="#F2C99A"/><ellipse cx="74" cy="108" rx="13" ry="17" fill="#fff"/><ellipse cx="126" cy="108" rx="13" ry="17" fill="#fff"/>
<path d="M90 134 q10 9 20 0"/><path d="M104 137 l3 8 l3 -7" fill="#fff" stroke-width="3"/></g>
<circle cx="76" cy="112" r="8" fill="{INK}"/><circle cx="124" cy="112" r="8" fill="{INK}"/><circle cx="56" cy="134" r="8" fill="{RED}" opacity=".5"/><circle cx="144" cy="134" r="8" fill="{RED}" opacity=".5"/></svg>'''
ART["teacher"] = f'''<svg viewBox="0 0 64 64" width="30" height="30" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M8 20 L32 10 L56 20 L32 30 Z" fill="{INK}"/><path d="M20 25 v8 q12 6 24 0 v-8"/><circle cx="24" cy="44" r="6"/><circle cx="40" cy="44" r="6"/><path d="M30 44 h4"/><path d="M27 55 q5 3 10 0"/><path d="M56 20 v12"/></g></svg>'''
