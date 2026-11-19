# template_v4 + build_v4 시험: python3 test_v4.py
#  - out4/site(새 판)를 저장소의 지난 그림(assets/)과 겹쳐 시험용 폴더에 놓고 로컬 http 서버로 엶
#  - 제2호는 publishAt 전이라 화면 규칙상 숨겨지므로, 시험에서만 editions/index.json 응답을 바꿔(route) 보여 줌
#  - 휴대폰 390×844, PC 1280×900 / 제1호(2026-11-17)·제2호(2026-11-20) / 가로 넘침·콘솔 오류·탭 이동
#  - 스도쿠 축하·왕관(새로 고침 뒤에도), 다 읽음 도장(너무 빨리 훑으면 안 찍힘), 퀴즈 채점, 시뮬레이터, 심리검사, 질문 단추
import asyncio, json, os, shutil, subprocess, sys, time, socket
from playwright.async_api import async_playwright

B = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(B)
SITE = os.path.join(B, "out4", "site"); SHOT = os.path.join(B, "out4", "test_shots")
TMP = os.environ.get("NOVA_TEST_DIR") or os.path.join(B, "out4", "_testroot")
PORT, ASKPORT = 8811, 8797
BASE = f"http://127.0.0.1:{PORT}/"
RESULTS = []
def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail)); print(("통과 " if cond else "실패 ") + name + (f" | {detail}" if detail else ""), flush=True)

def prepare():
    if os.path.exists(TMP): shutil.rmtree(TMP)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(TMP, "assets"))
    shutil.copytree(SITE, TMP, dirs_exist_ok=True)
    os.makedirs(SHOT, exist_ok=True)

def wait_port(p):
    for _ in range(50):
        try: socket.create_connection(("127.0.0.1", p), .2).close(); return
        except OSError: time.sleep(.1)

D2 = json.load(open(os.path.join(SITE, "editions", "2026-11-20.json"), encoding="utf-8"))
D1 = json.load(open(os.path.join(SITE, "editions", "2026-11-17.json"), encoding="utf-8"))
IDX = json.load(open(os.path.join(SITE, "editions", "index.json"), encoding="utf-8"))
for x in IDX["issues"]: x["publishAt"] = "2026-11-01T00:00:00+09:00"   # 시험용: 두 호 모두 공개된 것처럼

async def new_page(br, vp, ask_url=None, clock=False):
    ctx = await br.new_context(viewport=vp, device_scale_factor=2 if vp["width"] < 500 else 1)
    pg = await ctx.new_page()
    errs = []
    def on_console(m):
        if m.type == "error":
            u = (m.location or {}).get("url", "")
            if u and not u.startswith(BASE) and not u.startswith("data:"): return   # 바깥 글꼴·유튜브 등 시험 환경에서 막힌 것은 뺌
            if "Failed to load resource" in m.text and "127.0.0.1" not in u: return
            errs.append(m.text)
    pg.on("console", on_console); pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    async def idx_route(route): await route.fulfill(status=200, content_type="application/json", body=json.dumps(IDX, ensure_ascii=False))
    await pg.route("**/editions/index.json", idx_route)
    if ask_url is not None:
        async def cfg_route(route): await route.fulfill(status=200, content_type="application/javascript", body=f'window.SEOA_CONFIG = {{ gasUrl: "", askUrl: "{ask_url}" }};')
        await pg.route("**/config.js", cfg_route)
    await pg.route("https://**/*", lambda r: r.abort())   # 바깥 인터넷은 막고 시험
    if clock: await pg.clock.install()
    return ctx, pg, errs

async def overflow(pg): return await pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")

async def tabs_tour(br, vp, name, date, data):
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE + f"?d={date}"); await pg.wait_for_selector(".tab")
    label = await pg.eval_on_selector(".dateline b", "e => e.textContent")
    ok(f"[{name}] {date} 열림", data["issue"]["label"] in label, label)
    secs = [s["id"] for s in data["sections"]]
    tabs = await pg.eval_on_selector_all(".tab", "es => es.map(e => e.dataset.s)")
    ok(f"[{name}] {date} 탭 목록", tabs == secs, ",".join(tabs))
    worst = 0
    for s in secs:
        await pg.click(f'.tab[data-s="{s}"]'); await pg.wait_for_timeout(250)
        ov = await overflow(pg); worst = max(worst, ov)
        if ov > 1: ok(f"[{name}] {date} {s} 가로 넘침", False, f"{ov}px")
        if date == "2026-11-20" or s in ("cover", "sudoku", "mind"):
            await pg.screenshot(path=os.path.join(SHOT, f"{name}_{date}_{s}.png"), full_page=False)
    ok(f"[{name}] {date} 모든 탭 가로 넘침 없음", worst <= 1, f"최대 {worst}px")
    if date == "2026-11-20":
        await pg.click('.tab[data-s="art"]'); await pg.wait_for_timeout(600)
        await pg.evaluate("Promise.all(Array.from(document.images).map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))")
        n_art = await pg.eval_on_selector_all(".artimg img", "es => es.filter(i => i.naturalWidth > 0).length")
        n_dt = await pg.eval_on_selector_all(".dt img", "es => es.filter(i => i.naturalWidth > 0).length")
        ok(f"[{name}] 예술 2편 작품 그림·가까이 보기", n_art == 2 and n_dt == len(D2["articles"]["art"]["details"]) + len(D2["articles"]["art2"]["details"]), f"작품 {n_art}, 조각 {n_dt}")
        await pg.click('.tab[data-s="lit"]'); await pg.wait_for_timeout(300)
        for _ in range(3): await pg.evaluate("document.querySelectorAll('.book img').forEach(i => i.scrollIntoView())"); await pg.wait_for_timeout(300)
        nb = await pg.eval_on_selector_all(".book img", "es => es.filter(i => i.complete && i.naturalWidth > 0).length")
        ok(f"[{name}] 책 표지 3장", nb == 3, str(nb))
        arts = await pg.eval_on_selector_all("article.art", "es => es.length")
        await pg.click('.tab[data-s="science"]'); await pg.wait_for_timeout(300)
        n_sci = await pg.eval_on_selector_all("article.art", "es => es.length")
        ok(f"[{name}] 과학 탭 기사 2편", n_sci == 2, str(n_sci))
    ok(f"[{name}] {date} 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def solve_sudoku(pg, k, puzzle, solution):
    for r in range(len(puzzle)):
        for c in range(len(puzzle)):
            if puzzle[r][c] == 0:
                await pg.click(f'#sgrid-{k} .scell[data-r="{r}"][data-c="{c}"]')
                await pg.click(f'#spad-{k} button[data-n="{solution[r][c]}"]')

async def test_sudoku(br, vp, name):
    ctx, pg, errs = await new_page(br, vp)
    await pg.add_init_script("""(() => { window.__osc = 0; const AC = window.AudioContext; if (!AC) return;
      const o = AC.prototype.createOscillator; AC.prototype.createOscillator = function(){ window.__osc++; return o.call(this); }; })();""")
    await pg.goto(BASE + "?d=2026-11-20#sudoku"); await pg.wait_for_selector("#sgrid-1 .scell")
    ov = await overflow(pg); ok(f"[{name}] 9×9 스도쿠 가로 넘침 없음", ov <= 1, f"{ov}px")
    gw = await pg.eval_on_selector("#sgrid-0", "e => e.getBoundingClientRect().width")
    pw = await pg.eval_on_selector("#spad-0", "e => { const r = e.getBoundingClientRect(); return [r.left, r.right]; }")
    ok(f"[{name}] 9×9 판·숫자 단추가 화면 안", gw <= vp["width"] and pw[0] >= 0 and pw[1] <= vp["width"], f"판 {gw:.0f}px, 단추 {pw[0]:.0f}~{pw[1]:.0f}px")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_sudoku9_start.png"))
    P = D2["sudoku"]["puzzles"]
    # 틀린 답 먼저: 첫 판 마지막 빈칸에 틀린 수
    await solve_sudoku(pg, 0, P[0]["puzzle"], P[0]["solution"])
    await pg.wait_for_timeout(250)
    cele = await pg.query_selector(".cele"); crown = await pg.eval_on_selector("#crown-0", "e => e.classList.contains('ghost') ? 'none' : 'block'")
    fx = await pg.query_selector("canvas.fxcv"); osc = await pg.evaluate("window.__osc")
    ok(f"[{name}] 첫째 판 정답 → 축하·팡파레·왕관", bool(cele) and crown != "none" and bool(fx) and osc > 0, f"축하창 {bool(cele)}, 왕관 {crown}, 색종이 {bool(fx)}, 소리 음 {osc}개")
    await pg.wait_for_timeout(500)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_sudoku9_celebrate.png"))
    # 둘째 판: 한 칸 틀리게 채운 뒤 '다 채웠어요' → 오답 안내, 고치면 축하
    pz, sol = P[1]["puzzle"], P[1]["solution"]
    blanks = [(r, c) for r in range(9) for c in range(9) if pz[r][c] == 0]
    wrong_sol = [row[:] for row in sol]; r0, c0 = blanks[0]; wrong_sol[r0][c0] = sol[r0][c0] % 9 + 1
    await solve_sudoku(pg, 1, pz, wrong_sol)
    await pg.click('[data-sdcheck="1"]'); await pg.wait_for_timeout(200)
    msg = await pg.inner_text("#sdMsg-1"); nwrong = await pg.eval_on_selector_all("#sgrid-1 .scell.wrong", "es => es.length")
    c1 = await pg.eval_on_selector("#crown-1", "e => e.classList.contains('ghost') ? 'none' : 'block'")
    ok(f"[{name}] 둘째 판 틀리면 왕관 없음·틀린 칸 표시", "다시 보세요" in msg and c1 == "none" and nwrong == 1, f"{msg[:20]} / 틀린 칸 {nwrong}")
    await pg.click(f'#sgrid-1 .scell[data-r="{r0}"][data-c="{c0}"]'); await pg.click(f'#spad-1 button[data-n="{sol[r0][c0]}"]')
    await pg.wait_for_timeout(300)
    c1 = await pg.eval_on_selector("#crown-1", "e => e.classList.contains('ghost') ? 'none' : 'block'")
    ok(f"[{name}] 둘째 판 고치면 왕관", c1 != "none", c1)
    await pg.wait_for_timeout(2800)
    await pg.reload(); await pg.wait_for_selector("#sgrid-1 .scell")
    c0r = await pg.eval_on_selector("#crown-0", "e => e.classList.contains('ghost') ? 'none' : 'block'"); c1r = await pg.eval_on_selector("#crown-1", "e => e.classList.contains('ghost') ? 'none' : 'block'")
    tag = await pg.eval_on_selector("#ctag-0", "e => getComputedStyle(e).display")
    ok(f"[{name}] 새로 고침 뒤에도 왕관 두 개 남음", c0r != "none" and c1r != "none" and tag != "none", f"{c0r}, {c1r}")
    await pg.evaluate("document.querySelector('#crown-0').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_sudoku9_crown_after_reload.png"))
    # 제1호 6×6: 그대로 한 판, 다 맞히면 축하(왕관 없음), 기록이 섞이지 않음
    await pg.goto(BASE + "?d=2026-11-17#sudoku"); await pg.wait_for_selector("#sgrid-0 .scell")
    n1 = await pg.eval_on_selector_all("#sgrid-0 .scell", "es => es.length"); nb = await pg.eval_on_selector_all(".sdb", "es => es.length")
    ok(f"[{name}] 제1호 스도쿠는 6×6 한 판", n1 == 36 and nb == 1, f"칸 {n1}, 판 {nb}")
    s1 = D1["sudoku"]; await solve_sudoku(pg, 0, s1["puzzle"], s1["solution"]); await pg.wait_for_timeout(300)
    m = await pg.inner_text("#sdMsg-0"); cele = await pg.query_selector(".cele")
    ok(f"[{name}] 제1호 6×6 정답 → 완성·축하", "완성" in m and bool(cele), m[:20])
    ok(f"[{name}] 스도쿠 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_read(br, vp, name):
    ctx, pg, errs = await new_page(br, vp, clock=True)
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#a-gorilla .endmark")
    need = await pg.eval_on_selector("#a-gorilla", "e => +e.dataset.need")
    # 빠르게 훑기: 바로 끝으로 내려가 3초만 머묾
    await pg.evaluate("document.querySelector('#a-gorilla .endmark').scrollIntoView({block:'center'})")
    await pg.clock.run_for(3000); await pg.wait_for_timeout(100)
    on = await pg.eval_on_selector("#a-gorilla .rstamp", "e => e.classList.contains('on')")
    ok(f"[{name}] 너무 빨리 훑으면 도장 안 찍힘", not on, f"필요 {need}초 중 3초")
    # 위로 올라가 읽는 시간(기사가 화면에 보이는 동안) → 끝에 닿으면 도장
    await pg.evaluate("window.scrollTo(0, document.querySelector('#a-gorilla').offsetTop)")
    await pg.clock.run_for(need * 1000); await pg.wait_for_timeout(100)
    on = await pg.eval_on_selector("#a-gorilla .rstamp", "e => e.classList.contains('on')")
    ok(f"[{name}] 시간이 지나도 끝에 닿기 전에는 안 찍힘", not on)
    await pg.evaluate("document.querySelector('#a-gorilla .endmark').scrollIntoView({block:'center'})")
    await pg.wait_for_timeout(150); await pg.clock.run_for(1000); await pg.wait_for_timeout(200)
    on = await pg.eval_on_selector("#a-gorilla .rstamp", "e => e.classList.contains('on')")
    em = await pg.eval_on_selector("#a-gorilla .endmark", "e => e.classList.contains('done') && !!e.querySelector('.rstamp.press')")
    ok(f"[{name}] 끝까지 읽으면 제목 옆·기사 끝 도장", on and em)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_read_stamp_end.png"))
    await pg.evaluate("window.scrollTo(0, document.querySelector('#a-gorilla').offsetTop - 60)"); await pg.wait_for_timeout(100)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_read_stamp_title.png"))
    await pg.click('.tab[data-s="contents"]'); await pg.wait_for_timeout(200)
    marks = await pg.eval_on_selector_all(".toc-row .tread", "es => es.length"); bar = await pg.inner_text(".readbar")
    ok(f"[{name}] 차례에 읽음 표시", marks == 1 and "1" in bar, f"표시 {marks}개, '{bar.strip()}'")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_contents_read.png"))
    await pg.reload(); await pg.wait_for_selector(".toc-row")
    marks = await pg.eval_on_selector_all(".toc-row .tread", "es => es.length")
    ok(f"[{name}] 새로 고침 뒤에도 읽음 표시", marks == 1)
    # 제1호에서는 같은 기기라도 제2호 기록이 섞이지 않음(호마다 따로)
    await pg.goto(BASE + "?d=2026-11-17#contents"); await pg.wait_for_selector(".toc-row")
    m1 = await pg.eval_on_selector_all(".toc-row .tread", "es => es.length"); has_bar = await pg.query_selector(".readbar")
    ok(f"[{name}] 제1호 차례: 읽음 기록 따로(0개)·진행 막대 있음", m1 == 0 and bool(has_bar))
    ok(f"[{name}] 도장 시험 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_quiz(br, vp, name):
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE + "?d=2026-11-20#quiz"); await pg.wait_for_selector("[data-type]")
    for typ, lv, qs in [("news", "보통", D2["newsQuiz"]["보통"]), ("math", "보통", D2["mathQuiz"]["보통"]), ("news", "어려움", D2["newsQuiz"]["어려움"])]:
        await pg.click(f'[data-type="{typ}"]'); await pg.click(f'[data-l="{lv}"]')
        for q in qs:
            if q["type"] == "mc": await pg.click(f'#quizBox [data-a="{q["answer"]}"]')
            elif q["type"] == "ox": await pg.click(f'#quizBox [data-a="{q["answer"]}"]')
            elif typ == "math":
                for ch in str(q["answer"]): await pg.click(f'#quizBox [data-k="{ch}"]')
                await pg.click('#quizBox [data-k="확인"]')
            else:
                await pg.fill("#tin", str(q["answer"])); await pg.click("#tok")
            await pg.click("#nx")
        res = await pg.inner_text("#quizBox")
        ok(f"[{name}] 퀴즈 채점 {typ} {lv} 모두 정답", f"{len(qs)} / {len(qs)}" in res, res.split("\n")[1] if "\n" in res else res[:20])
        await pg.click("#again")
    # 틀린 답 한 번
    await pg.click('[data-type="news"]'); await pg.click('[data-l="쉬움"]')
    q = D2["newsQuiz"]["쉬움"][0]
    bad = (q["answer"] + 1) % len(q["options"]) if q["type"] == "mc" else ("X" if q["answer"] == "O" else "O")
    await pg.click(f'#quizBox [data-a="{bad}"]'); t = await pg.inner_text("#fb")
    ok(f"[{name}] 퀴즈 틀린 답 안내", "아쉬워요" in t and "정답" in t)
    ok(f"[{name}] 퀴즈 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_sims(br, vp, name):
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE + "?d=2026-11-20#math"); await pg.wait_for_selector("#foldSim")
    for _ in range(3): await pg.click("#foldW" if _ % 2 == 0 else "#foldH"); await pg.wait_for_timeout(520)
    st = await pg.inner_text("#foldStat")
    await pg.click("#foldOpen"); await pg.wait_for_timeout(100); m = await pg.inner_text("#foldMsg")
    ok(f"[{name}] 접기 시뮬레이터(3번 → 8겹, 펼치면 8칸)", "3번 접음" in st and "8겹" in st and "8칸" in m, st)
    await pg.fill("#foldIm", "42"); await pg.dispatch_event("#foldIm", "input"); im = await pg.inner_text("#foldImOut")
    ok(f"[{name}] 상상 접기 42번 → 달", "달" in im, im[:40])
    await pg.evaluate("document.querySelector('#foldSim').scrollIntoView()"); await pg.screenshot(path=os.path.join(SHOT, f"{name}_sim_folding.png"))
    await pg.click('#snowSim [data-a="flipR"]'); await pg.wait_for_timeout(500); await pg.click('#snowSim [data-a="flipD"]'); await pg.wait_for_timeout(500)
    j = await pg.inner_text("#snowJudge")
    ok(f"[{name}] 눈송이 시뮬레이터(뒤집기 둘 = 180° 돌리기)", "180°" in j, j)
    await pg.click("#snowEx"); await pg.wait_for_timeout(100); cnt = await pg.inner_text("#snowCount")
    ok(f"[{name}] 눈송이 그리기판 보기 예시 → 12조각", "12" in cnt, cnt)
    await pg.evaluate("document.querySelector('#snowSim').scrollIntoView()"); await pg.screenshot(path=os.path.join(SHOT, f"{name}_sim_snowflake.png"))
    ov = await overflow(pg); ok(f"[{name}] 수학 탭(시뮬레이터 둘) 가로 넘침 없음", ov <= 1, f"{ov}px")
    # 제1호 연필 돌리기 시뮬레이터도 그대로
    await pg.goto(BASE + "?d=2026-11-17#math"); await pg.wait_for_selector("#simCv")
    await pg.fill("#simR", "180"); await pg.dispatch_event("#simR", "input"); await pg.wait_for_timeout(100)
    c = await pg.inner_text("#simC")
    ok(f"[{name}] 제1호 연필 돌리기 시뮬레이터", "칸" in c, c)
    ok(f"[{name}] 시뮬레이터 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_psy(br, vp, name):
    ctx, pg, errs = await new_page(br, vp)
    for date, kick, lab in [("2026-11-20", "나의 짝꿍 유형", "이런 짝과 만나면 좋아요"), ("2026-11-17", "나의 탐구 유형", "닮은 과학자")]:
        await pg.goto(BASE + f"?d={date}#mind"); await pg.wait_for_selector("#psyDone")
        n = len((D2 if date.endswith("20") else D1)["articles"]["psytest"]["questions"])
        for i in range(n): await pg.click(f'.psy[data-q="{i}"] >> nth=0')
        await pg.click("#psyDone"); t = await pg.inner_text("#psyRes")
        ok(f"[{name}] 심리검사 {date} 결과 문구", kick in t and lab in t, t.split("\n")[0])
    ok(f"[{name}] 심리검사 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_ask(br, vp, name):
    # (가) askUrl 없음
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#askBtn")
    await pg.click("#askBtn"); await pg.fill("#qIn", "고릴라는 왜 손가락 마디로 걸어요?"); await pg.click("#qSend")
    t = await pg.inner_text("#qAns")
    ok(f"[{name}] 질문: 서버 없을 때 안내", "아직 답하는 서버가 연결되지 않았어요" in t, t[:30])
    await ctx.close()
    # (나) 가짜 로컬 서버(nova_ask.py, NOVA_FAKE=1)
    ctx, pg, errs = await new_page(br, vp, ask_url=f"http://127.0.0.1:{ASKPORT}/ask")
    seen = {}
    async def slow(route):
        seen["body"] = route.request.post_data; seen["ct"] = route.request.headers.get("content-type")
        await asyncio.sleep(1.2); await route.continue_()
    await pg.route(f"http://127.0.0.1:{ASKPORT}/ask", slow)
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#askBtn")
    await pg.click("#askBtn"); await pg.fill("#qIn", "별 두 개가 합쳐지면 어떻게 돼요?"); await pg.click("#qSend")
    await pg.wait_for_timeout(300); w = await pg.inner_text("#qAns")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_ask_wait.png"))
    await pg.wait_for_selector("#qAns .ans:not(.wait)", timeout=8000); t = await pg.inner_text("#qAns")
    body = json.loads(seen.get("body") or "{}")
    ok(f"[{name}] 질문: 생각 중 표시 → 답 표시", "생각 중" in w and "시험용 답" in t, t[:40])
    ok(f"[{name}] 질문: text/plain POST, 본문 {{q, issue}}", (seen.get("ct") or "").startswith("text/plain") and body.get("q") and body.get("issue") == 2, json.dumps(body, ensure_ascii=False)[:80])
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_ask_answer.png"))
    # 300자 제한(화면)
    await pg.fill("#qIn", "가" * 400); v = await pg.eval_on_selector("#qIn", "e => e.value.length")
    ok(f"[{name}] 질문 300자 제한(화면)", v == 300, str(v))
    ok(f"[{name}] 질문 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()
    # (다) 서버가 꺼져 있을 때
    ctx, pg, errs = await new_page(br, vp, ask_url="http://127.0.0.1:9/ask")
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#askBtn")
    await pg.click("#askBtn"); await pg.fill("#qIn", "질문"); await pg.click("#qSend")
    await pg.wait_for_selector("#qAns .ans.err", timeout=8000); t = await pg.inner_text("#qAns")
    ok(f"[{name}] 질문: 서버 실패 시 친절한 오류", "답을 받지 못했어요" in t, t[:40])
    await ctx.close()

async def test_figimg(br):
    """figs의 img: 그림 파일을 보여 주고 '일러스트'·credit 표시, img가 없는 그림은 예전처럼(SVG 있으면 SVG)"""
    ctx, pg, errs = await new_page(br, {"width": 390, "height": 844})
    d = json.loads(json.dumps(D2)); g = d["articles"]["gorilla"]
    g["figs"][0]["img"] = "n2_art_d0"; g["figs"][0]["credit"] = "그림: Nova 편집부 의뢰, AI 생성 일러스트"
    d["figs"]["gorilla_2"] = '<svg viewBox="0 0 10 5" xmlns="http://www.w3.org/2000/svg"><rect width="10" height="5" fill="#1F3A5F"/></svg>'
    d["cover"]["img"] = "n2_art_0"
    async def ed(route): await route.fulfill(status=200, content_type="application/json", body=json.dumps(d, ensure_ascii=False))
    await pg.route("**/editions/2026-11-20.json", ed)
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#a-gorilla figure")
    await pg.wait_for_timeout(500)
    r = await pg.evaluate("""() => { const f = document.querySelectorAll('#a-gorilla figure');
      return [f.length, !!f[0].querySelector('img') && f[0].querySelector('img').naturalWidth > 0, f[0].querySelector('.illu') && f[0].querySelector('.illu').textContent, (f[0].querySelector('.credit')||{}).textContent, !!f[1].querySelector('svg')]; }""")
    ok("[그림] figs.img → 그림 파일 + 일러스트 표시 + credit, 다음 그림은 SVG", r[0] == 2 and r[1] and r[2] == "일러스트" and "AI 생성" in (r[3] or "") and r[4], str(r))
    await pg.evaluate("document.querySelector('#a-gorilla figure').scrollIntoView()"); await pg.screenshot(path=os.path.join(SHOT, "phone_fig_img_test.png"))
    await pg.click('.tab[data-s="cover"]'); await pg.wait_for_timeout(400)
    cimg = await pg.eval_on_selector(".c-art img.c-img", "e => e.naturalWidth > 0")
    ok("[그림] 표지 그림 파일(cover.img)", cimg)
    ok("[그림] 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_inline(br):
    ctx = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); pg = await ctx.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.route("https://**/*", lambda r: r.abort())
    await pg.goto("file://" + os.path.join(B, "out4", "index.html")); await pg.wait_for_selector(".tab")
    worst = 0
    for s in [x["id"] for x in D2["sections"]]:
        await pg.click(f'.tab[data-s="{s}"]'); await pg.wait_for_timeout(150); worst = max(worst, await overflow(pg))
    await pg.click('.tab[data-s="art"]'); await pg.wait_for_timeout(300)
    n = await pg.eval_on_selector_all(".artimg img", "es => es.filter(i => i.src.startsWith('data:')).length")
    ok("[아티팩트 한 파일] 모든 탭·그림 내장·오류 없음", worst <= 1 and n == 2 and not errs, f"넘침 {worst}px, 작품 {n}, 오류 {errs[:2]}")
    await pg.click('.tab[data-s="math"]'); await pg.wait_for_timeout(300)
    sims = await pg.evaluate("[!!document.querySelector('#foldSim'), !!document.querySelector('#snowSim'), Object.keys(window.__NOVA_SIMS__ || {}).length]")
    await pg.click("#foldW"); await pg.wait_for_timeout(550); st = await pg.inner_text("#foldStat")
    ok("[아티팩트 한 파일] 시뮬레이터(eval 없이 내장 스크립트)", sims == [True, True, 2] and "2겹" in st, f"{sims} {st}")
    await pg.click('.tab[data-s="cover"]'); await pg.wait_for_timeout(200); await pg.screenshot(path=os.path.join(SHOT, "inline_phone_cover.png"))
    await ctx.close()

async def main():
    prepare()
    web = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=TMP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env = dict(os.environ, NOVA_FAKE="1", NOVA_ALLOW_LOCAL="1", NOVA_PORT=str(ASKPORT)); env.pop("ANTHROPIC_API_KEY", None)
    ask = subprocess.Popen([sys.executable, os.path.join(B, "site", "ask_server", "nova_ask.py")], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait_port(PORT); wait_port(ASKPORT)
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
            for name, vp in [("phone", {"width": 390, "height": 844}), ("pc", {"width": 1280, "height": 900})]:
                await tabs_tour(br, vp, name, "2026-11-20", D2)
                await tabs_tour(br, vp, name, "2026-11-17", D1)
                await test_sudoku(br, vp, name)
                await test_read(br, vp, name)
                await test_sims(br, vp, name)
                if name == "phone":
                    await test_quiz(br, vp, name); await test_psy(br, vp, name)
                await test_ask(br, vp, name)
            await test_figimg(br)
            await test_inline(br)
            await br.close()
    finally:
        web.terminate(); ask.terminate()
    bad = [r for r in RESULTS if not r[1]]
    print(f"\n결과: {len(RESULTS) - len(bad)} / {len(RESULTS)} 통과" + ("" if not bad else "\n실패: " + "\n  ".join(f"{n} | {d}" for n, _, d in bad)))
    sys.exit(1 if bad else 0)

asyncio.run(main())
