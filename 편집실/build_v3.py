# Nova 제1호 3판 조립: v3/*.json(없으면 v2) → 아티팩트용 한 파일 + GitHub Pages용 사이트
import json, os, random, sys, base64, shutil
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
from art_v2 import ART
V = os.path.join(B, "v2")
V3 = os.path.join(B, "v3")
FROM = {}
def L(n):
    for d, tag in ((V3, "v3"), (V, "v2")):
        p = os.path.join(d, n + ".json")
        if os.path.exists(p):
            FROM[n] = tag; return json.load(open(p, encoding="utf-8"))
    return None
import glob as _g
KO = {}
for _f in sorted(_g.glob(os.path.join(V, "ko_summaries*.json"))):
    try: KO.update(json.load(open(_f, encoding="utf-8")))
    except Exception as _e: print("국문 요약 읽기 실패:", _f, _e)
FIX = json.load(open(os.path.join(V, "fixes.json"), encoding="utf-8")) if os.path.exists(os.path.join(V, "fixes.json")) else {}
# 만화는 GPT 이미지 모델 그림을 기다림(편집부 선화는 쓰지 않음)
# 표지 그림: 한 화면 표지에서 위아래·양옆 빈자리까지 밤하늘이 이어지도록 바탕을 넓힘
def _wide_cover(s):
    s = s.replace('<svg viewBox="0 0 800 560"', '<svg overflow="visible" viewBox="0 0 800 560"', 1)
    s = s.replace('<rect width="800" height="560" fill="#FBF8F1"/>', '', 1)
    s = s.replace('<rect x="0" y="0" width="800" height="560" fill="#1F3A5F"/>', '<rect x="-1600" y="-2000" width="4000" height="4560" fill="#1F3A5F"/>', 1)
    s = s.replace('<rect x="0" y="0" width="800" height="560" fill="url(#dot)" opacity=".35"/>', '<rect x="-1600" y="-2000" width="4000" height="4560" fill="url(#dot)" opacity=".35"/>', 1)
    rr = random.Random(7); st = []
    while len(st) < 260:
        x, y = rr.uniform(-1600, 2400), rr.uniform(-2000, 2560)
        if 0 <= x <= 800 and 0 <= y <= 560: continue
        st.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr.choice([0.8,1.4,2.0])}" fill="#F4EFE4"/>')
    i = s.find('</defs>') + len('</defs>')
    j = s.find('<circle', i)
    return s[:j] + "".join(st) + s[j:]
ART["cover"] = _wide_cover(ART["cover"])

IDS = ["voyager", "leonid", "crow", "dino", "kelp", "icecube", "kakeya", "economy", "art", "cute", "psytest", "comic"]
A, missing, MISS = {}, [], []
for i in IDS:
    d = L(i)
    if d is None: missing.append(i); continue
    if FROM.get(i) == "v3":   # 3판: 사실 검수 고치기 → 편집장(쉬운 말) 고치기 순서로
        for _ff in ("fact_fixes.json", "fable_fixes.json"):
            _p = os.path.join(V3, _ff)
            if not os.path.exists(_p): continue
            _fx = json.load(open(_p, encoding="utf-8")).get(i, {})
            _s = json.dumps(d, ensure_ascii=False)
            for old, new in _fx.get("replace", []):
                o, n = json.dumps(old, ensure_ascii=False)[1:-1], json.dumps(new, ensure_ascii=False)[1:-1]
                if o in _s: _s = _s.replace(o, n, 1)
                else: MISS.append((_ff, i, old[:40]))
            d = json.loads(_s)
            have = {t["w"] for t in d.get("terms", [])}
            for t in _fx.get("terms_add", []):
                if t["w"] not in have: d.setdefault("terms", []).append(t); have.add(t["w"])
    if i in FIX and FROM.get(i) == "v2":   # 2판 원고에만 2판 고치기 적용
        for old, new in FIX[i].get("replace", []):
            hit = False
            for b in d.get("body", []):
                if "x" in b and old in b["x"]: b["x"] = b["x"].replace(old, new); hit = True
            if not hit and old in json.dumps(d, ensure_ascii=False):
                d = json.loads(json.dumps(d, ensure_ascii=False).replace(json.dumps(old, ensure_ascii=False)[1:-1], json.dumps(new, ensure_ascii=False)[1:-1])); hit = True
            if not hit: print("고치기 못 찾음:", i, old[:30])
        for k, v in FIX[i].get("set", {}).items(): d[k] = v
    for s in d.get("sources", []):
        if s.get("lang") == "en" and s.get("u") in KO: s["ko"] = KO[s["u"]]
    # 객관식 보기 순서 섞기(정답이 늘 같은 자리에 있지 않게)
    _qr = random.Random("nova-" + i)
    for lv, qs in (d.get("quiz") or {}).items():
        for q in qs:
            if q.get("type") == "mc" and isinstance(q.get("answer"), int):
                opts = list(enumerate(q["options"])); _qr.shuffle(opts)
                q["answer"] = [k for k, (o, _) in enumerate(opts) if o == q["answer"]][0]
                q["options"] = [x for _, x in opts]
    d = json.loads(json.dumps(d, ensure_ascii=False).replace("서아 페이퍼", "Nova"))
    A[i] = d

# 책: 평점·리뷰·판매 지표로 고른 원고(books2)가 있으면 그것을 씀
_bk2 = os.path.join(B, "drafts", "books2.json")
books = json.load(open(_bk2 if os.path.exists(_bk2) else os.path.join(B, "drafts", "books.json"), encoding="utf-8"))
METRICS = json.load(open(os.path.join(B, "src", "books2", "metrics.json"), encoding="utf-8"))
books.update({"kicker": books.get("corner", "이번 주 책"), "deck": books.get("sub", "")})
COV = {"405005952": "sm_405005952.jpg", "405996842": "sm_405996842.jpg", "406235825": "sm_406235825.jpg",
       "263027170": "sm_263027170.jpg", "362545754": "sm_362545754.jpg", "273246838": "sm_273246838.jpg"}
for b in books["books"]:
    iid = b["url"].split("ItemId=")[-1]; b["cover_file"] = COV.get(iid)
    m = METRICS.get(b["title"])
    if m: b["metrics"] = m
A["books"] = books

SECTIONS = [
  {"id": "cover", "name": "표지"},
  {"id": "contents", "name": "차례", "en": "CONTENTS", "desc": "이번 호에 실린 것", "kind": "contents"},
  {"id": "science", "name": "과학", "en": "SCIENCE", "desc": "이번 주 과학 뉴스와 특집", "items": ["voyager", "leonid", "crow", "dino", "kelp", "icecube"]},
  {"id": "math", "name": "수학", "en": "MATHEMATICS", "desc": "깊이 읽기", "items": ["kakeya"]},
  {"id": "economy", "name": "경제", "en": "ECONOMY", "desc": "경제 깊이 읽기", "items": ["economy"]},
  {"id": "art", "name": "예술", "en": "ART", "desc": "그림 읽기", "items": ["art"]},
  {"id": "lit", "name": "문학", "en": "BOOKS", "desc": "이번 주 책", "items": ["books"]},
  {"id": "mind", "name": "심리검사", "en": "MIND", "desc": "재미로 보는 검사와 마음의 과학", "items": ["psytest", "cute"]},
  {"id": "comic", "name": "만화", "en": "COMICS", "desc": "Nova 만화", "items": ["comic"]},
  {"id": "sudoku", "name": "스도쿠", "en": "PUZZLE", "desc": "두뇌 놀이", "kind": "sudoku"},
  {"id": "quiz", "name": "퀴즈", "en": "QUIZ", "desc": "기사 퀴즈와 수학 퀴즈", "kind": "quiz"},
  {"id": "video", "name": "영상", "en": "VIDEO", "desc": "이번 주 영상", "kind": "video"},
  {"id": "chiikawa", "name": "먼작귀", "en": "CHIIKAWA", "desc": "먼작귀 신간", "kind": "chiikawa"},
]
for s in SECTIONS:
    s["items"] = [i for i in s.get("items", []) if i in A]
# 쪽 번호(잡지 느낌): 글 길이로 대략
def plen(i):
    a = A.get(i, {}); n = sum(len(b.get("x", "")) for b in a.get("body", []))
    return max(2, round(n / 550)) if i not in ("books", "comic", "psytest") else 4
page, toc, figc = 4, [], 0
for s in SECTIONS[1:]:
    if s.get("kind") == "contents": continue
    start = page
    s["figStart"] = figc
    for i in s.get("items", []):
        a = A[i]; toc.append({"sec": s["name"], "t": a["title"], "p": str(page), "go": s["id"]}); page += plen(i)
        figc += 1
    if s.get("kind"):
        toc.append({"sec": s["name"], "t": {"sudoku": "6×6 스도쿠", "quiz": "기사 퀴즈·수학 퀴즈", "video": "이번 주 영상", "chiikawa": "이번 주 먼작귀"}[s["kind"]], "p": str(page), "go": s["id"]}); page += 2
    s["pages"] = f"{start}–{page-1}"

vy = A.get("voyager", {})
COVER = {
  "headline": vy.get("title", ""), "lead": [vy.get("deck", "")], "go": "science",
  "caption": "보이저 1호는 11월 18일 저녁, 지구에서 빛으로 하루 걸리는 곳에 닿아요.",
  "lines": [{"sec": "특집", "t": A["icecube"]["title"], "go": "science"} if "icecube" in A else None,
            {"sec": "수학", "t": A["kakeya"]["title"], "go": "math"} if "kakeya" in A else None,
            {"sec": "경제", "t": A["economy"]["title"], "go": "economy"} if "economy" in A else None,
            {"sec": "예술", "t": A["art"]["title"], "go": "art"} if "art" in A else None,
            {"sec": "과학", "t": A["crow"]["title"], "go": "science"} if "crow" in A else None,
            {"sec": "마음", "t": A["cute"]["title"], "go": "mind"} if "cute" in A else None,
            {"sec": "문학", "t": A["books"]["title"], "go": "lit"} if "books" in A else None,
            ],
}
COVER["lines"] = [x for x in COVER["lines"] if x]

# 기사 퀴즈: 난이도마다 10문제, 기사마다 고르게
rng = random.Random(20261117); pool = {"쉬움": [], "보통": [], "어려움": []}
for i in IDS:
    for lv, qs in (A.get(i, {}).get("quiz") or {}).items():
        for q in qs: q["from"] = i; pool.setdefault(lv, []).append(q)
NQ = {}
for lv, qs in pool.items():
    by = {}
    for q in qs: by.setdefault(q["from"], []).append(q)
    pick = []
    while len(pick) < 10 and any(by.values()):
        for k in list(by):
            if by[k] and len(pick) < 10: pick.append(by[k].pop(0))
    rng.shuffle(pick); NQ[lv] = pick

math = json.load(open(os.path.join(B, "math_quiz.json"), encoding="utf-8"))["levels"]
sud = json.load(open(os.path.join(B, "sudoku.json"), encoding="utf-8"))
extra = json.load(open(os.path.join(B, "extra.json"), encoding="utf-8"))
_vids = json.load(open(os.path.join(V3, "videos.json"), encoding="utf-8")) if os.path.exists(os.path.join(V3, "videos.json")) else []
_TN = {"그림": "그려 보기", "만들기": "만들어 보기", "과학": "실험해 보기", "기사연결": "기사와 함께 보기"}
for v in _vids: v["topicName"] = _TN.get(v.get("topic"), v.get("topic", ""))
VIDEO = {
  "kicker": "이번 주 영상", "title": "그리고, 만들고, 실험하고, 더 알아보는 영상 네 편",
  "deck": "주제가 겹치지 않게 네 편을 골랐어요. 많은 사람이 본 영상 가운데, 방송사나 오래 활동한 어린이 채널의 영상을 먼저 봤어요.",
  "body": [{"t": "p", "x": "영상은 유튜브 검색 결과에서 조회수(본 사람 수)와 올린 지 얼마나 됐는지, 어떤 채널이 만들었는지를 살펴 골랐어요. 오래전에 올라왔어도 지금 봐도 좋은 내용이면 골랐어요. 유튜브에는 별점이 없고, 좋아요 수와 댓글은 이번에 확인하지 못했어요."}],
  "list": _vids, "checked": "2026년 11월 17일",
}
CHI = dict(extra["chiikawa"]); CHI["deck"] = "번역하지 않고, 공식 계정에 올라온 원본을 그대로 소개해요."
ASK = extra["askPrompt"].replace("어린이 신문 '서아 페이퍼'", "과학 교양지 'Nova'").replace("4학년이 이해할 수 있는 쉬운 말로, '~해요'체로 3~6문장으로 답해.", "초등학교 4학년이 이해할 수 있게 '~해요'체로 4~8문장으로 쉽고 자세하게 답해. 비유를 하나 이상 들고, 4학년이 모를 것 같은 낱말은 괄호 안에 쉬운 뜻을 붙여. 내용은 정확하게, 모르는 것은 모른다고 말해.")

from PIL import Image as _Im
import io as _io, subprocess as _sp
IMGD = os.path.join(B, "img3"); os.makedirs(IMGD, exist_ok=True)
IMAGES = {}   # 키 → 파일 경로
def _save(im, name, maxw):
    im = im.convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), _Im.LANCZOS)
    p = os.path.join(IMGD, name); im.save(p, quality=80, optimize=True); return p
for aid in ["art"]:
    a = A.get(aid) or {}
    for k, w in enumerate(a.get("artworks", [])):
        raw = os.path.join(IMGD, f"{aid}_{k}_raw")
        if not os.path.exists(raw) and w.get("image_url"):
            _sp.run(["curl", "-sL", "-A", "Mozilla/5.0 (Nova magazine build; contact via GitHub)", "-o", raw, w["image_url"]])
        try:
            im = _Im.open(raw); im.load()
        except Exception as e:
            print("작품 그림 받기 실패:", w.get("image_url"), e); continue
        IMAGES[f"{aid}_{k}"] = _save(im, f"{aid}_{k}.jpg", 1200)
        if k == 0:
            for d, dt in enumerate(a.get("details", [])):
                x, y, ww, hh = [float(dt[z]) for z in ("x", "y", "w", "h")]
                box = (round(x*im.width), round(y*im.height), round((x+ww)*im.width), round((y+hh)*im.height))
                IMAGES[f"{aid}_d{d}"] = _save(im.crop(box), f"{aid}_d{d}.jpg", 560)
CM = os.path.join(B, "comic_gpt")
if os.path.isdir(CM):
    for f in sorted(os.listdir(CM)):
        n, ext = os.path.splitext(f)
        if ext.lower() in (".png", ".jpg", ".jpeg", ".webp") and (n.startswith("comic_") ):
            IMAGES[n] = _save(_Im.open(os.path.join(CM, f)), n + ".jpg", 1400)
def _uri(p): return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

def data(embed, cover_src):
    bk = json.loads(json.dumps(A["books"], ensure_ascii=False))
    for b in bk["books"]:
        f = b.pop("cover_file", None)
        b["img"] = cover_src(f) if f else ""
    arts = dict(A); arts["books"] = bk
    return {
      "issue": {"no": 1, "label": "제1호 · 창간호", "date": "2026-11-17", "dateText": "2026년 11월 17일 화요일", "dateShort": "2026. 11. 17", "publishAt": "2026-11-17T20:00:00+09:00"},
      "sections": SECTIONS, "articles": arts, "figs": ART, "cover": COVER, "toc": toc,
      "editorNote": "Nova는 초등학교 4학년 서아가 직접 기획한 과학 잡지예요. 일주일에 한 번, 금요일 밤 10시에 나와요. 'Nova(노바)'는 '새로 밝게 빛나는 별'이라는 뜻이에요. 밤하늘에 갑자기 나타난 새 별처럼, 매주 새로운 궁금증을 하나씩 밝혀 보려고 해요. 읽다가 궁금한 것이 생기면 오른쪽 아래 '무엇이든 물어보세요'를 눌러 물어보세요.",
      "newsQuiz": NQ, "mathQuiz": math, "quizNote": "수학 퀴즈는 4학년 2학기 범위로 임시 출제했어요. 아빠가 문제 파일을 주시면 거기에 맞춰요. 정답은 모두 컴퓨터로 계산해 확인했어요.",
      "sudoku": sud, "video": VIDEO, "chiikawa": CHI, "askPrompt": ASK, "embed": embed,
      "images": {k: (_uri(p) if not embed else "assets/img/" + os.path.basename(p)) for k, p in IMAGES.items()},
    }

tpl = open(os.path.join(B, "template_v3.html"), encoding="utf-8").read()
CD = os.path.join(B, "covers")
def b64(f): return "data:image/jpeg;base64," + base64.b64encode(open(os.path.join(CD, f), "rb").read()).decode()
art_data = data(False, b64)
js = json.dumps(art_data, ensure_ascii=False).replace("</", "<\\/")
html = tpl.replace('<script src="config.js" onerror="void 0"></script>\n', '').replace("/*__BOOT__*/", "window.__INLINE__ = " + js + ";")
os.makedirs(os.path.join(B, "out3"), exist_ok=True)
open(os.path.join(B, "out3", "index.html"), "w", encoding="utf-8").write(html)
json.dump(art_data, open(os.path.join(B, "out3", "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# GitHub Pages 정식판
site = os.path.join(B, "site3"); ed = os.path.join(site, "editions"); cv = os.path.join(site, "assets", "covers")
os.makedirs(ed, exist_ok=True); os.makedirs(cv, exist_ok=True)
for f in COV.values(): shutil.copy(os.path.join(CD, f), os.path.join(cv, f))
os.makedirs(os.path.join(site, "assets", "img"), exist_ok=True)
for p in IMAGES.values(): shutil.copy(p, os.path.join(site, "assets", "img", os.path.basename(p)))
open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(tpl.replace("/*__BOOT__*/", ""))
sd = data(True, lambda f: "assets/covers/" + f)
json.dump(sd, open(os.path.join(ed, "2026-11-17.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"issues": [{"no": 1, "date": "2026-11-17", "label": "제1호 · 창간호", "dateText": "2026년 11월 17일 화요일", "publishAt": "2026-11-17T20:00:00+09:00", "file": "2026-11-17.json"}]}, open(os.path.join(ed, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in ["config.js", ".nojekyll", "README.md"]:
    src = os.path.join(B, "site", f)
    if os.path.exists(src): shutil.copy(src, os.path.join(site, f))
os.makedirs(os.path.join(site, "apps_script"), exist_ok=True)
shutil.copy(os.path.join(B, "site", "apps_script", "Code.gs"), os.path.join(site, "apps_script", "Code.gs"))
print("고치기 못 찾음:", MISS or "없음")
print("원고 출처:", {k: v for k, v in FROM.items()})
print("조립 완료", len(html) // 1024, "KB | 없는 원고:", missing or "없음", "| 퀴즈:", {k: len(v) for k, v in NQ.items()})
