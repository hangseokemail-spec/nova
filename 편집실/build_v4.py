# Nova 제2호 조립(v4)
#   원고: issues/2026-11-20/final/ (없으면 drafts/, 파일마다 final에 없으면 drafts에서 찾음)
#   출력: out4/index.html (Claude 아티팩트 미리보기용 한 파일)
#         out4/site/ (깃허브 페이지용: index.html, config.js, editions/2026-11-20.json, editions/index.json, assets/img/n2_*.jpg)
#   템플릿: template_v4.html (제1호 데이터도 그대로 열려요)
# 그림 넣는 곳(있으면 자동으로 씀)
#   issues/2026-11-20/figs/<기사id>.svg, <기사id>_2.svg, cover.svg  : 편집부 SVG 도판(art_v2.py 형식으로 만든 것)
#   issues/2026-11-20/img/Nova2_g<번호>_*.png                       : GPT 일러스트 → 기사 figs에 {"img":"n2_g<번호>", ...}
#   issues/2026-11-20/img/Nova2_cover*.png                          : 표지 그림(4:5) → n2_cover.jpg
#   issues/2026-11-20/comic/comic_<칸>.png                          : comic_slice.py로 자른 만화 칸
import json, os, random, sys, base64, shutil, re, glob, subprocess
from PIL import Image

B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
ROOT = os.path.dirname(B)                      # 저장소 맨 위
DATE = "2026-11-20"
ISSUE = {"no": 2, "label": "제2호", "date": DATE, "dateText": "2026년 11월 20일 금요일", "dateShort": "2026. 11. 20",
         "publishAt": "2026-11-20T22:00:00+09:00"}
PFX = "n2_"                                    # 이번 호 그림 파일 이름 앞머리(지난 호와 겹치지 않게)
ID = os.path.join(B, "issues", DATE)
FINAL, DRAFTS = os.path.join(ID, "final"), os.path.join(ID, "drafts")
SRC_DIRS = [d for d in (FINAL, DRAFTS) if os.path.isdir(d)]
OUT = os.path.join(B, "out4"); SITE = os.path.join(OUT, "site"); IMG_OUT = os.path.join(SITE, "assets", "img")
os.makedirs(IMG_OUT, exist_ok=True)

FROM = {}
def src_path(name):
    for d in SRC_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p): FROM[name] = os.path.basename(d); return p
    return None
def L(name):
    p = src_path(name)
    return json.load(open(p, encoding="utf-8")) if p else None

# ---------------- 도판(SVG) ----------------
from art_v2 import ART as ART1, svg as _svg, stars as _stars
FIGS = {"mascot": ART1["mascot"], "teacher": ART1["teacher"]}   # 제1호 기사 도판은 넣지 않음(id가 겹치는 economy·art 주의)
for f in sorted(glob.glob(os.path.join(ID, "figs", "*.svg"))):
    FIGS[os.path.splitext(os.path.basename(f))[0]] = open(f, encoding="utf-8").read()
if os.path.exists(os.path.join(ID, "art_n2.py")):              # 편찬 때 만든 도판 모듈이 있으면 합침
    import importlib.util
    sp = importlib.util.spec_from_file_location("art_n2", os.path.join(ID, "art_n2.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    FIGS.update({k: v for k, v in m.ART.items() if k not in ("mascot", "teacher")})
if "n2_cover" in FIGS: FIGS["cover"] = FIGS["n2_cover"]   # 도판 담당이 그린 표지(4:5)
if "cover" not in FIGS:   # 임시 표지: 밤하늘에 가까이 붙은 별 둘(주제 '둘이 만나면'). 표지 그림이 오면 바뀜
    rr = random.Random(20261120)
    st = "".join(f'<circle cx="{rr.uniform(-1600,2400):.0f}" cy="{rr.uniform(-2000,2560):.0f}" r="{rr.choice([0.8,1.3,1.9])}" fill="#F4EFE4" opacity="{rr.choice([.5,.8,1])}"/>' for _ in range(520))
    FIGS["cover"] = (f'<svg overflow="visible" viewBox="0 0 800 560" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="cg"><stop offset="0" stop-color="#F4EFE4"/><stop offset=".35" stop-color="#E3B448" stop-opacity=".55"/><stop offset="1" stop-color="#E3B448" stop-opacity="0"/></radialGradient>'
                     f'<pattern id="cdot" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="#1C1A17" opacity=".55"/></pattern></defs>'
                     f'<rect x="-1600" y="-2000" width="4000" height="4560" fill="#1F3A5F"/><rect x="-1600" y="-2000" width="4000" height="4560" fill="url(#cdot)" opacity=".35"/>{st}'
                     f'<circle cx="372" cy="210" r="120" fill="url(#cg)"/><circle cx="452" cy="232" r="80" fill="url(#cg)"/>'
                     f'<circle cx="372" cy="210" r="22" fill="#F4EFE4"/><circle cx="452" cy="232" r="13" fill="#F4EFE4"/>'
                     f'<path d="M300 260 Q410 140 520 205" fill="none" stroke="#C8372D" stroke-width="2.5" stroke-dasharray="6 7"/></svg>')

# ---------------- 원고 ----------------
IDS = ["gorilla", "merger", "folding", "snowflake", "economy", "export", "art", "art2", "purr", "psytest", "comic"]
A, missing, MISS, FIG_MISSING = {}, [], [], []
for i in IDS:
    d = L(i + ".json")
    if d is None: missing.append(i); continue
    for _ff in ("fact_fixes.json", "fable_fixes.json"):   # 사실 고치기 → 쉬운 말 고치기 순서(파일이 있을 때만)
        _p = os.path.join(ID, _ff)
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
    _qr = random.Random("nova-" + DATE + "-" + i)   # 객관식 보기 섞기
    for lv, qs in (d.get("quiz") or {}).items():
        for q in qs:
            if q.get("type") == "mc" and isinstance(q.get("answer"), int):
                opts = list(enumerate(q["options"])); _qr.shuffle(opts)
                q["answer"] = [k for k, (o, _) in enumerate(opts) if o == q["answer"]][0]
                q["options"] = [x for _, x in opts]
    d.pop("facts", None); d.pop("gpt_prompt", None); d.pop("image", None)   # 화면에 쓰지 않는 조사 기록은 싣지 않음
    for p_ in d.get("panels", []) or []: p_.pop("place_note", None)
    heads = {b.get("x") for b in d.get("body", []) or [] if b.get("t") == "h"}
    keep = []
    for f in d.get("figs", []) or []:
        f.pop("brief", None)
        if f.get("svg") and f["svg"] not in FIGS:   # 도판 파일이 아직 없으면 그 그림만 건너뜀
            FIG_MISSING.append((i, f["svg"])); continue
        if "at" in f and f["at"] and f["at"] not in heads and i != "psytest":
            print("그림 자리(at) 소제목을 못 찾아 기사 끝에 둠:", i, f.get("svg") or f.get("img"), f["at"]); f["at"] = ""
        keep.append(f)
    if "figs" in d: d["figs"] = keep
    d = json.loads(json.dumps(d, ensure_ascii=False).replace("서아 페이퍼", "Nova"))
    A[i] = d

# 만화: 7칸의 '…'와 '톡.'은 그림을 보고 정한 자리(칸 왼쪽 위에서 가로 %, 세로 %)
COMIC_POS = {(7, "…"): (33, 70), (7, "톡."): (28, 52)}
if "comic" in A:
    for k, p_ in enumerate(A["comic"].get("panels", []), 1):
        for l in p_.get("lines", []):
            if (k, l.get("say")) in COMIC_POS: l["pos"] = list(COMIC_POS[(k, l["say"])])

# 책
books = L("books.json"); METRICS = L("books_metrics.json") or {}
COV = {}
if books:
    books.update({"kicker": books.get("corner", "이번 주 책"), "deck": books.get("sub", "")})
    books.pop("facts", None)
    for b in books["books"]:
        iid = b["url"].split("ItemId=")[-1]
        f = os.path.join(ID, "covers", f"sm_{iid}.jpg")
        if os.path.exists(f): COV[iid] = f; b["cover_file"] = iid
        m = METRICS.get(b["title"])
        if m: b["metrics"] = m
    A["books"] = books
else: missing.append("books")

# ---------------- 쪽 구성 ----------------
SECTIONS = [
  {"id": "cover", "name": "표지"},
  {"id": "contents", "name": "차례", "en": "CONTENTS", "desc": "이번 호에 실린 것", "kind": "contents"},
  {"id": "science", "name": "과학", "en": "SCIENCE", "desc": "이번 주 과학 뉴스", "items": ["gorilla", "merger"]},
  {"id": "math", "name": "수학", "en": "MATHEMATICS", "desc": "깊이 읽기 두 편", "items": ["folding", "snowflake"]},
  {"id": "economy", "name": "경제", "en": "ECONOMY", "desc": "경제 깊이 읽기와 뉴스 읽기", "items": ["economy", "export"]},
  {"id": "art", "name": "예술", "en": "ART", "desc": "그림 읽기 두 편", "items": ["art", "art2"]},
  {"id": "lit", "name": "문학", "en": "BOOKS", "desc": "이번 주 책", "items": ["books"]},
  {"id": "mind", "name": "심리검사", "en": "MIND", "desc": "재미로 보는 검사와 좋아하는 것", "items": ["psytest", "purr"]},
  {"id": "comic", "name": "만화", "en": "COMICS", "desc": "Nova 만화", "items": ["comic"]},
  {"id": "sudoku", "name": "스도쿠", "en": "PUZZLE", "desc": "두뇌 놀이", "kind": "sudoku"},
  {"id": "quiz", "name": "퀴즈", "en": "QUIZ", "desc": "기사 퀴즈와 수학 퀴즈", "kind": "quiz"},
  {"id": "video", "name": "영상", "en": "VIDEO", "desc": "이번 주 영상", "kind": "video"},
]
for s in SECTIONS: s["items"] = [i for i in s.get("items", []) if i in A]
sud = L("sudoku.json")
KIND_T = {"sudoku": (f"9×9 스도쿠 {len(sud['puzzles'])}판" if sud and "puzzles" in sud else "스도쿠"), "quiz": "기사 퀴즈·수학 퀴즈", "video": "이번 주 영상"}
def plen(i):
    a = A.get(i, {}); n = sum(len(b.get("x", "")) for b in a.get("body", []))
    return max(2, round(n / 550)) if i not in ("books", "comic", "psytest") else 4
page, toc, figc = 4, [], 0
for s in SECTIONS[1:]:
    if s.get("kind") == "contents": continue
    start = page; s["figStart"] = figc
    for i in s.get("items", []):
        toc.append({"sec": s["name"], "t": A[i]["title"], "p": str(page), "go": s["id"], "id": i}); page += plen(i); figc += 1
    if s.get("kind"):
        toc.append({"sec": s["name"], "t": KIND_T[s["kind"]], "p": str(page), "go": s["id"]}); page += 2
    s["pages"] = f"{start}–{page-1}"

# 표지: 큰 제목 「둘이 만나면 생기는 일」, 머리기사 gorilla. 편집장의 final/editor.json이 있으면 그 문구를 씀
ED = L("editor.json") or {}
head = A.get("gorilla", {})
SEC_OF = {i: (s["name"], s["id"]) for s in SECTIONS for i in s.get("items", [])}
def cover_line(x):
    if isinstance(x, str) and x in A: return {"sec": {"심리검사": "마음"}.get(SEC_OF[x][0], SEC_OF[x][0]) if x in SEC_OF else "", "t": A[x]["title"], "go": SEC_OF.get(x, ("", "contents"))[1]}
    if isinstance(x, dict):
        i = x.get("id")
        if i in A: return {"sec": x.get("sec") or SEC_OF.get(i, ("",))[0], "t": x.get("t") or A[i]["title"], "go": x.get("go") or SEC_OF.get(i, ("", "contents"))[1]}
        if x.get("t"): return {"sec": x.get("sec", ""), "t": x["t"], "go": x.get("go", "contents")}
    return None
LINE_IDS = ["merger", "folding", "economy", "art", "purr", "books"]   # 탭마다 한 줄씩
COVER = {"kicker": "이번 호 주제", "headline": ED.get("coverTitle") or "둘이 만나면 생기는 일",
         "lead": [ED.get("coverLead") or head.get("deck", "")], "go": "science",
         "caption": ED.get("coverCaption") or "리샤가 받침이 되고 아멜리아가 손을 뻗었어요. 하늘에는 큰 별과 작은 별이 함께 있어요.",
         "lines": [l for l in (cover_line(x) for x in (ED.get("coverLines") or LINE_IDS)) if l]}
if "n2_cover" in FIGS: COVER["fit"] = "xMidYMax slice"   # 4:5 표지 도판은 칸을 꽉 채우고 아래(땅)를 맞춤
if not ED: print("알림: final/editor.json이 없어 표지 문구와 편집장 글은 임시 문구예요.")

# 기사 퀴즈: 난이도마다 10문제, 기사마다 고르게
rng = random.Random(20261120); pool = {"쉬움": [], "보통": [], "어려움": []}
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

math_q = L("math_quiz.json") or {"levels": {}}
extra = json.load(open(os.path.join(B, "extra.json"), encoding="utf-8"))
vids = L("videos.json") or []
_TN = {"그림": "그려 보기", "만들기": "만들어 보기", "과학": "실험해 보기", "기사연결": "기사와 함께 보기"}
for v in vids: v["topicName"] = _TN.get(v.get("topic"), v.get("topic", ""))
VIDEO = {
  "kicker": "이번 주 영상", "title": "그리고, 만들고, 실험하고, 더 알아보는 영상 네 편",
  "deck": "주제가 겹치지 않게 네 편을 골랐어요. 많은 사람이 본 영상 가운데, 방송사나 오래 활동한 어린이 채널의 영상을 먼저 봤어요.",
  "body": [{"t": "p", "x": "영상은 11월 19일 유튜브 검색 결과에서 조회수, 올린 때, 채널을 보고 골랐어요. 영상을 끝까지 재생해 확인하지 못했어요. 좋아요·댓글 수는 읽지 못했어요. 영상 속 광고는 Nova가 고를 수 없으니 어른과 함께 보세요."}],
  "list": vids, "checked": "2026년 11월 19일",
}
ASK = extra["askPrompt"].replace("어린이 신문 '서아 페이퍼'", "과학 교양지 'Nova'").replace("4학년이 이해할 수 있는 쉬운 말로, '~해요'체로 3~6문장으로 답해.", "초등학교 4학년이 이해할 수 있게 '~해요'체로 4~8문장으로 쉽고 자세하게 답해. 비유를 하나 이상 들고, 4학년이 모를 것 같은 낱말은 괄호 안에 쉬운 뜻을 붙여. 내용은 정확하게, 모르는 것은 모른다고 말해.")

# ---------------- 시뮬레이터: <id>_sim.html에서 CSS와 함수만 뽑아 호 데이터에 실음 ----------------
BASE_SEL = (":root", "html", "body", ".wrap", ".sim{", ".sim-head", ".sim-goal")
def load_sim(sid):
    p = src_path(sid + "_sim.html")
    if not p: return None
    h = open(p, encoding="utf-8").read()
    css = re.search(r"<style>(.*?)</style>", h, re.S).group(1)
    css = "\n".join(l for l in css.splitlines() if l.strip() and not l.strip().startswith("/*") and not l.strip().startswith(BASE_SEL))
    js = re.findall(r"<script>(.*?)</script>", h, re.S)[-1]
    js = "\n".join(l for l in js.splitlines() if "simMount" not in l and not re.match(r"^\s*bind\w*\(\);\s*$", l))
    fh = re.search(r"function\s+(\w+Html)\s*\(", js).group(1); fb = re.search(r"function\s+(bind\w+)\s*\(", js).group(1)
    return {"css": css, "js": js, "html": fh, "bind": fb}
SIMS = {}
for i, a in A.items():
    for b in a.get("body", []) or []:
        if b.get("t") == "sim" and b.get("x") and b["x"] != "kakeya":
            s = load_sim(b["x"])
            if s: SIMS[b["x"]] = s
            else: print("시뮬레이터 파일 없음:", b["x"])

# ---------------- 그림 ----------------
IMAGES = {}   # 화면 키 → 저장한 파일 경로
def save_img(im, name, maxw):
    im = im.convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    p = os.path.join(IMG_OUT, name); im.save(p, quality=80, optimize=True); return p
# 작품 그림(예술 두 편 모두): 기자가 받아 둔 1920px 축소본을 먼저 쓰고, 없으면 위키미디어에서 받음
ART_LOCAL = {("art", 0): "art_0.jpg", ("art2", 0): "art_1.jpg"}
for aid in ("art", "art2"):
    a = A.get(aid) or {}
    for k, w in enumerate(a.get("artworks", [])):
        raw = os.path.join(ID, "img_src", ART_LOCAL.get((aid, k), f"{aid}_{k}.jpg"))
        if not os.path.exists(raw) and (w.get("image_url_1920") or w.get("image_url")):
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0 (Nova magazine build; contact via GitHub)", "-o", raw, w.get("image_url_1920") or w["image_url"]])
        try: im = Image.open(raw); im.load()
        except Exception as e: print("작품 그림 없음:", aid, k, e); continue
        IMAGES[f"{aid}_{k}"] = save_img(im, f"{PFX}{aid}_{k}.jpg", 1200)
        if k == 0:
            for d, dt in enumerate(a.get("details", [])):
                x, y, ww, hh = [float(dt[z]) for z in ("x", "y", "w", "h")]
                box = (round(x*im.width), round(y*im.height), round(min(1, x+ww)*im.width), round(min(1, y+hh)*im.height))
                IMAGES[f"{aid}_d{d}"] = save_img(im.crop(box), f"{PFX}{aid}_d{d}.jpg", 560)
# 기사 일러스트(figs의 img): issues/<날짜>/img/ 에서 이름으로 찾음. 없으면 img를 빼서 SVG 도판이나 빈자리로 돌아감
IMGD = os.path.join(ID, "img")
def find_src(key):
    if not os.path.isdir(IMGD): return None
    m = re.match(r"n(\d+)_g(\d+)$", key)
    for f in sorted(os.listdir(IMGD)):
        st, ext = os.path.splitext(f)
        if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp"): continue
        if st == key or (m and re.match(rf"Nova{m.group(1)}_g{m.group(2)}(_|$)", st)): return os.path.join(IMGD, f)
    return None
for i, a in A.items():
    for f in a.get("figs", []) or []:
        if not f.get("img"): continue
        s = find_src(f["img"])
        if s: IMAGES[f["img"]] = save_img(Image.open(s), f["img"] + ".jpg", 1600)
        else: print("그림 파일 없음(그림 빼고 조립):", i, f["img"]); f.pop("img")
cov_src = [p for p in sorted(glob.glob(os.path.join(IMGD, "Nova2_cover*"))) if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
if cov_src:
    IMAGES[PFX + "cover"] = save_img(Image.open(cov_src[0]), PFX + "cover.jpg", 1400); COVER["img"] = PFX + "cover"
CM = os.path.join(ID, "comic")
if os.path.isdir(CM):
    for f in sorted(os.listdir(CM)):
        n, ext = os.path.splitext(f)
        if ext.lower() in (".png", ".jpg", ".jpeg", ".webp") and re.match(r"comic_(\d+|page)$", n):
            IMAGES[n] = save_img(Image.open(os.path.join(CM, f)), PFX + n + ".jpg", 1400)
for iid, f in COV.items():
    IMAGES["cover_" + iid] = shutil.copy(f, os.path.join(IMG_OUT, f"{PFX}cover_{iid}.jpg"))
USED = {"cover", "mascot", "teacher"}
for a in A.values():
    for f in (a.get("figs") or []) if isinstance(a, dict) else []:
        if f.get("svg"):
            USED.add(f["svg"]); USED.add(f["svg"] + "_h")
            if a.get("id") == "psytest" or a is A.get("psytest"): USED.update(f["svg"] + "_" + c for c in "abcd")
FIGS = {k: v for k, v in FIGS.items() if k in USED or not k.startswith("n2_")}
FIGS.pop("n2_cover", None)
def _uri(p): return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

def data(embed):
    src = (lambda p: "assets/img/" + os.path.basename(p)) if embed else _uri
    arts = json.loads(json.dumps(A, ensure_ascii=False))
    if "books" in arts:
        for b in arts["books"]["books"]:
            iid = b.pop("cover_file", None)
            b["img"] = src(IMAGES["cover_" + iid]) if iid else ""
    return {
      "issue": ISSUE, "sections": SECTIONS, "articles": arts, "figs": FIGS, "cover": COVER, "toc": toc,
      "editorNote": ED.get("editorNote") or "Nova는 초등학교 4학년 서아가 직접 기획한 과학 잡지예요. 일주일에 한 번, 금요일 밤 10시에 나와요. 이번 호의 주제는 '둘이 만나면'이에요. 고릴라 둘이 사다리가 되고, 별 둘이 하나로 합쳐지고, 종이는 접을 때마다 2배가 돼요. 기사를 끝까지 읽으면 '잘했어요' 도장이 찍혀요. 읽다가 궁금한 것이 생기면 오른쪽 아래 '무엇이든 물어보세요'를 눌러 물어보세요.",
      "newsQuiz": NQ, "mathQuiz": math_q["levels"],
      "quizNote": "수학 퀴즈는 이번 호 수학 기사 두 편과 4학년 2학기 범위에서 냈어요. 아빠가 문제 파일을 주시면 거기에 맞춰요.",
      "sudoku": sud, "video": VIDEO, "askPrompt": ASK, "askExample": "예: 고릴라는 왜 손가락 마디로 땅을 짚나요?",
      "sims": SIMS, "embed": embed,
      "images": {k: src(p) for k, p in IMAGES.items() if not k.startswith("cover_")},
    }

tpl = open(os.path.join(B, "template_v4.html"), encoding="utf-8").read()
assert "/*__BOOT__*/" in tpl and '<script src="config.js" onerror="void 0"></script>\n' in tpl
inline = data(False)
js = json.dumps(inline, ensure_ascii=False).replace("</", "<\\/")
# 한 파일 미리보기에서는 시뮬레이터 코드를 eval 없이 쓰도록 <script>로 바로 넣음(아티팩트 보안 설정 대비)
pre = "window.__NOVA_SIMS__ = {" + ",".join(f'{json.dumps(k)}: (function(){{\n{v["js"]}\nreturn {{html: {v["html"]}, bind: {v["bind"]}}};\n}})()' for k, v in SIMS.items()) + "};\n"
html = tpl.replace('<script src="config.js" onerror="void 0"></script>\n', '').replace("/*__BOOT__*/", pre.replace("</", "<\\/") + "window.__INLINE__ = " + js + ";")
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
json.dump(inline, open(os.path.join(OUT, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 깃허브 페이지 묶음
ed = os.path.join(SITE, "editions"); os.makedirs(ed, exist_ok=True)
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(tpl.replace("/*__BOOT__*/", ""))
json.dump(data(True), open(os.path.join(ed, f"{DATE}.json"), "w", encoding="utf-8"), ensure_ascii=False)
idx = json.load(open(os.path.join(ROOT, "editions", "index.json"), encoding="utf-8"))   # 지난 호를 지우지 않고 덧붙임
idx["issues"] = [x for x in idx["issues"] if x.get("date") != DATE] + [{k: ISSUE[k] for k in ("no", "date", "label", "dateText", "publishAt")} | {"file": f"{DATE}.json"}]
json.dump(idx, open(os.path.join(ed, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in idx["issues"]:   # 함께 시험하려고 지난 호 파일도 옆에 둠(저장소에 이미 있는 그대로)
    p = os.path.join(ROOT, "editions", x["file"])
    if x["date"] != DATE and os.path.exists(p): shutil.copy(p, os.path.join(ed, x["file"]))
# config.js: gasUrl은 지금 값 그대로, askUrl 칸을 더함(서버 주소는 편집인이 서버를 켠 뒤 넣어요)
cfg_old = open(os.path.join(ROOT, "config.js"), encoding="utf-8").read()
gas = (re.search(r'gasUrl\s*:\s*"([^"]*)"', cfg_old) or [None, ""])[1]
ask = (re.search(r'askUrl\s*:\s*"([^"]*)"', cfg_old) or [None, ""])[1]
open(os.path.join(SITE, "config.js"), "w", encoding="utf-8").write(
    "// gasUrl: 시트 기록용 Apps Script 웹 앱 주소. 비어 있으면 기기 안에만 기록한다.\n"
    "// askUrl: '무엇이든 물어보세요'에 바로 답하는 서버 주소(예: https://3-34-169-45.sslip.io/ask). 비어 있으면 '아직 연결되지 않았어요' 안내만 한다.\n"
    f'window.SEOA_CONFIG = {{ gasUrl: "{gas}", askUrl: "{ask}" }};\n')

print("원고 출처:", FROM)
print("도판:", len(glob.glob(os.path.join(ID, "figs", "*.svg"))), "개 파일 | 빠진 도판:", FIG_MISSING or "없음")
print("고치기 못 찾음:", MISS or "없음")
print("시뮬레이터:", list(SIMS), "| 그림:", sorted(IMAGES))
print("조립 완료", len(html) // 1024, "KB | 없는 원고:", missing or "없음", "| 퀴즈:", {k: len(v) for k, v in NQ.items()})
