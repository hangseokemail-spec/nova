# Nova 주제 데이터베이스: 이미 다룬 주제·책·영상·작품을 모으고, 새 후보가 겹치는지 대조해요.
#
#   python3 편집실/topic_db.py build
#       editions/*.json(나온 호 전부)을 읽어 편집실/topics_db.json 과 topics_db.csv 를 다시 만들어요.
#       편집실/issues/*/drafts/_보류/ 의 원고는 '보류'로 따로 적어요(아직 안 실린 주제라 다시 써도 돼요).
#
#   python3 편집실/topic_db.py check 후보.json
#       후보.json: [{"kind":"article|book|video|art", "section":"과학", "title":"...", "keywords":["...", ...],
#                    "urls":["출처 주소"], "video_id":"...", "book_title":"...", "artist":"...", "artwork":"..."}]
#       후보마다 지난 호와 겹치는 정도를 보여 주고, 판정(배제 / 비슷함-검토 / 통과)을 붙여요.
#       결과 표는 기획안에 그대로 붙여요.
#
#   python3 편집실/topic_db.py q "고릴라 협력"      (빠르게 한 줄로 찾아보기)
#
# 판정 기준(README_오퍼스4인.md 2절과 같아요)
#   배제: 같은 영상 id, 같은 책 제목, 같은 작품(작가+제목), 같은 출처 주소, 또는 비슷함 점수 0.45 이상
#   비슷함-검토: 점수 0.25 이상이거나 핵심 낱말 2개 이상이 겹침 → 편집장이 '다른 각도'인지 판단하고, 아니면 배제
#   통과: 그 밖
import glob, json, os, re, sys, csv

B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
DBJ, DBC = os.path.join(B, "topics_db.json"), os.path.join(B, "topics_db.csv")

STOP = set("이번 우리 그리고 하는 있는 했다 했어요 이에요 예요 무엇 어떻게 왜 까닭 이야기 기사 처음 새 다시 가장 아주 한 두 세 것 수 등 더 때 및 의 를 을 이 가 은 는 에 에서 와 과 로 으로 만에 하나 둘 셋 년 월 일 아래 위 속 안 밖 옆 앞 뒤 마리 사람 모습 위해 통해 대해 정말 어떤 무슨 누구 언제 어디 얼마나 만큼 동안 모두 함께 서로 지금 오늘 새로 쉬운 쉽게".split())
# 어느 기사에나 나오는 낱말(주제 겹침으로 치지 않음)
GENERIC = set("논문 학술지 관측 분석 연구 연구진 연구팀 과학 과학자 문학 방송 그림 그리기 만들기 읽기 천천히 구도 kbs ebs 1억 2배 마법사 어린이 어린 실험 sub how toy diy 영상 소개 그리 쉬운 팡팡 놀이터 호기심".split())

def clean(s):
    return re.sub(r"<[^>]+>", " ", str(s or ""))

def words(s):
    """제목·풀이에서 핵심 낱말 뽑기(2글자 이상, 조사 떼기)."""
    out = []
    for w in re.findall(r"[0-9A-Za-z가-힣]+", clean(s)):
        w = re.sub(r"(으로|에서|에게|까지|부터|처럼|보다|이에요|예요|이다|했다|했어요|하는|하다|은|는|이|가|을|를|의|에|와|과|도|만|로)$", "", w)
        if len(w) >= 2 and w not in STOP:
            out.append(w.lower())
    return out

def bigrams(s):
    t = re.sub(r"[^0-9A-Za-z가-힣]", "", clean(s).lower())
    return {t[i:i + 2] for i in range(len(t) - 1)}

def jacc(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0

def entry(**k):
    k.setdefault("keywords", []); k.setdefault("urls", [])
    return k

def from_issue(d, status="실림"):
    iss = d.get("issue", {}); no, date = iss.get("no"), iss.get("date")
    secname = {}
    for s in d.get("sections", []):
        for i in s.get("items", []) or []:
            secname[i] = s.get("name", "")
    out = []
    for aid, a in (d.get("articles") or {}).items():
        if aid == "books":
            for b in a.get("books", []):
                out.append(entry(issue=no, date=date, status=status, kind="book", section="문학", id="book",
                                 title=b.get("title", ""), keywords=words(b.get("title", "")) + words(b.get("field", "")),
                                 urls=[u for u in [b.get("url")] if u], book_title=b.get("title", ""), by=b.get("by", "")))
            continue
        kw = [t.get("w", "") for t in a.get("terms", []) or []]
        kw += words(a.get("title", ""))
        rec = entry(issue=no, date=date, status=status, kind="article", section=secname.get(aid, a.get("section", "")),
                    id=aid, title=a.get("title", ""), deck=clean(a.get("deck", ""))[:200],
                    keywords=sorted(set(k for k in kw if k)), urls=[s.get("u") for s in a.get("sources", []) or [] if s.get("u")])
        if aid == "comic":
            rec["kind"] = "comic"
        if aid == "psytest":
            rec["kind"] = "psytest"
        out.append(rec)
        for w in a.get("artworks", []) or []:
            out.append(entry(issue=no, date=date, status=status, kind="art", section="예술", id=aid,
                             title=w.get("title", ""), artwork=w.get("title", ""), artist=w.get("artist", ""),
                             keywords=words(w.get("title", "")) + words(w.get("artist", "")),
                             urls=[u for u in [w.get("commons_page")] if u]))
    for v in (d.get("video") or {}).get("list", []) or []:
        vid = v.get("id") or ""
        out.append(entry(issue=no, date=date, status=status, kind="video", section="영상", id="video", title=v.get("title", ""),
                         video_id=vid, channel=v.get("channel", ""), keywords=words(v.get("title", "")) + words(v.get("topic", "")),
                         urls=["https://www.youtube.com/watch?v=" + vid] if vid else []))
    return out

def build():
    db = []
    for f in sorted(glob.glob(os.path.join(R, "editions", "*.json"))):
        if f.endswith("index.json"):
            continue
        db += from_issue(json.load(open(f, encoding="utf-8")))
    # 보류 원고(아직 안 실림): 다음 호 후보로 다시 쓸 수 있어요
    for f in sorted(glob.glob(os.path.join(B, "issues", "*", "drafts", "_보류", "*.json"))):
        try:
            a = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(a, dict) or not a.get("title"):
            continue
        date = f.split(os.sep)[-4]
        db.append(entry(issue=None, date=date, status="보류", kind="article", section=a.get("section", ""), id=a.get("id", ""),
                        title=a.get("title", ""), deck=clean(a.get("deck", ""))[:200],
                        keywords=sorted(set([t.get("w", "") for t in a.get("terms", []) or []] + words(a.get("title", "")))),
                        urls=[s.get("u") for s in a.get("sources", []) or [] if s.get("u")]))
    json.dump({"note": "Nova에 실린 주제·책·영상·작품 목록. topic_db.py build 로 다시 만들어요. status '보류'는 아직 안 실린 원고예요.",
               "entries": db}, open(DBJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(DBC, "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["호", "발행일", "상태", "종류", "쪽", "원고 id", "제목", "핵심 낱말", "영상 id·책·작품", "출처 주소"])
        for e in db:
            extra = e.get("video_id") or e.get("book_title") or (e.get("artist", "") + " " + e.get("artwork", "")).strip()
            w.writerow([e.get("issue") or "", e.get("date", ""), e["status"], e["kind"], e.get("section", ""), e.get("id", ""),
                        e.get("title", ""), " · ".join(e.get("keywords", [])[:12]), extra, " | ".join(e.get("urls", []))])
    n = sum(1 for e in db if e["status"] == "실림")
    print(f"주제 데이터베이스: 실림 {n}개, 보류 {len(db) - n}개 → {DBJ}")

def load():
    if not os.path.exists(DBJ):
        build()
    return json.load(open(DBJ, encoding="utf-8"))["entries"]

def stem(k):
    k = k.lower()
    return re.sub(r"(기|을|를|는|은|이|가|의|에|들)$", "", k) if len(k) >= 3 else k

def compare(c, db):
    ctext = c.get("title", "") + " " + " ".join(c.get("keywords", []))
    cb = bigrams(ctext)
    ck = {stem(k) for k in c.get("keywords", []) + words(c.get("title", "")) if len(stem(k)) >= 2}
    curls = set(c.get("urls", []))
    res = []
    for e in db:
        if e["status"] != "실림":
            continue
        why = []
        if c.get("video_id") and c["video_id"] == e.get("video_id"):
            why.append("같은 영상")
        if c.get("book_title") and e.get("book_title") and re.sub(r"\s", "", c["book_title"]) == re.sub(r"\s", "", e["book_title"]):
            why.append("같은 책")
        if c.get("artwork") and e.get("artwork") and (re.sub(r"\s", "", c["artwork"])[:6] == re.sub(r"\s", "", e["artwork"])[:6]):
            why.append("같은 작품")
        if curls & set(e.get("urls", [])) and e["kind"] == "article":
            why.append("같은 출처")
        full = (e.get("title", "") + " " + e.get("deck", "") + " " + " ".join(e.get("keywords", []))).lower()
        eb = bigrams(full)
        contain = len(cb & eb) / len(cb) if cb else 0.0          # 후보 글자 조각이 지난 기사에 얼마나 들어 있나
        shared = sorted(k for k in ck if k in full and k not in GENERIC)
        et = e.get("title", "").lower()
        title_hit = sorted(k for k in {stem(w) for w in words(c.get("title", ""))} if len(k) >= 2 and k not in GENERIC and k in et)
        score = max(jacc(cb, bigrams(e.get("title", "") + " " + " ".join(e.get("keywords", [])))), 0.6 * contain)
        shared = sorted(set(shared) | set(title_hit))
        e = dict(e, _title_hit=title_hit)
        res.append((score, shared, why, e))
    res.sort(key=lambda r: (bool(r[2]), r[0] + 0.12 * len(r[1])), reverse=True)
    top = res[:3]
    verdict = "통과"
    for score, shared, why, e in top:
        th = e.get("_title_hit", [])
        lexical_only = e["kind"] in ("video", "book", "art") or c.get("kind") in ("video", "book", "art")
        if why or (not lexical_only and (score >= 0.45 or len(th) >= 2)):
            verdict = "배제"; break   # 영상·책·작품은 같은 것일 때만 배제, 글자만 비슷하면 검토
        if score >= 0.22 or len(th) >= 1 or len(shared) >= 3:
            verdict = "비슷함-검토"
    return verdict, top

def show(cands, db):
    lines = ["| 후보 | 판정 | 가장 비슷한 지난 주제 (점수, 겹친 낱말·까닭) |", "|---|---|---|"]
    for c in cands:
        v, top = compare(c, db)
        near = "<br>".join(f"제{e.get('issue')}호 {e.get('section','')} 「{e.get('title','')[:40]}」 ({s:.2f}, {', '.join(why + shared[:4]) or '-'})"
                           for s, shared, why, e in top)
        lines.append(f"| {c.get('section','')} · {c.get('title','')} | **{v}** | {near} |")
    print("\n".join(lines))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "check":
        show(json.load(open(sys.argv[2], encoding="utf-8")), load())
    elif cmd == "q":
        q = " ".join(sys.argv[2:]); show([{"title": q, "keywords": words(q)}], load())
    else:
        sys.exit("사용법: build | check 후보.json | q \"찾을 말\"")
