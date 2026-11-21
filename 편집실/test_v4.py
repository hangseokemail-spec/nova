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
SEOA_CODE = "별빛 서아7"   # 시험용 서아 확인 암호(진짜 암호는 서버에서 편집인이 넣어요)
ASKDATA = os.path.join(B, "out4", "_askdata")
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

async def new_page(br, vp, ask_url=None, clock=False, idx=None):
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
    async def idx_route(route): await route.fulfill(status=200, content_type="application/json", body=json.dumps(idx or IDX, ensure_ascii=False))
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
    body = await pg.evaluate("document.body.innerText + ' ' + document.title")
    ok(f"[{name}] {date} 제호에 '서아가 기획한 주간 과학 교양지' 없음·<title> Nova", "주간 과학 교양지" not in body.replace(" ", "") and "주 간 과 학 교 양 지" not in body and (await pg.title()) == "Nova" and "노바(Nova)" in await pg.content())
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
    # (가) askUrl 없음(저장소 config.js에는 주소가 있으니 시험에서만 빈 값으로)
    ctx, pg, errs = await new_page(br, vp, ask_url="")
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
    g["figs"][0] = {"img": "n2_art_d0", "at": g["figs"][0]["at"], "cap": "시험용 그림 설명", "credit": "그림: Nova 편집부 의뢰, AI 생성 일러스트"}   # GPT 그림이 SVG 자리를 대신하는 경우
    d["cover"]["img"] = "n2_art_0"
    async def ed(route): await route.fulfill(status=200, content_type="application/json", body=json.dumps(d, ensure_ascii=False))
    await pg.route("**/editions/2026-11-20.json", ed)
    await pg.goto(BASE + "?d=2026-11-20#science"); await pg.wait_for_selector("#a-gorilla figure")
    await pg.wait_for_timeout(500)
    r = await pg.evaluate("""() => { const f = document.querySelectorAll('#a-gorilla .body figure');
      return [f.length, !!f[0].querySelector('img') && f[0].querySelector('img').naturalWidth > 0, f[0].querySelector('.illu') && f[0].querySelector('.illu').textContent, (f[0].querySelector('.credit')||{}).textContent, !!f[1].querySelector('svg')]; }""")
    ok("[그림] figs.img(at 자리) → 그림 파일 + 일러스트 표시 + credit, 다음 그림은 SVG", r[0] == 3 and r[1] and r[2] == "일러스트" and "AI 생성" in (r[3] or "") and r[4], str(r))
    await pg.evaluate("document.querySelector('#a-gorilla figure').scrollIntoView()"); await pg.screenshot(path=os.path.join(SHOT, "phone_fig_img_test.png"))
    await pg.click('.tab[data-s="cover"]'); await pg.wait_for_timeout(400)
    cimg = await pg.eval_on_selector(".c-art img.c-img", "e => e.naturalWidth > 0")
    ok("[그림] 표지 그림 파일(cover.img)", cimg)
    ok("[그림] 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

# 만화 칸마다 가리면 안 되는 곳(감·까마귀, 칸 안 %: 왼, 위, 오른, 아래). 그림을 직접 보고 정함
PROTECT = {1: [(55, 3, 70, 20)], 2: [(49, 3, 64, 21), (75, 50, 98, 78)], 3: [(66, 3, 81, 20)], 4: [(59, 3, 74, 20)],
           5: [(62, 3, 78, 20)], 6: [(59, 3, 74, 21)], 7: [(69, 6, 82, 24), (76, 3, 90, 27)]}

async def test_final(br, vp, name):
    """최종 원고 화면: 본문 안 도판, 표지, 만화 대사, 심리 동점, 경제 알림, 책 고른 방법, 스도쿠 규칙, 영상 안내"""
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE + "?d=2026-11-20#cover"); await pg.wait_for_selector(".c-art")
    h = await pg.inner_text(".c-head h2"); sv = await pg.query_selector(".c-art svg")
    ok(f"[{name}] 표지: 큰 제목·표지 도판", h.strip() == "둘이 만나면 생기는 일" and bool(sv), h)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_final_cover.png"))
    # 과학: 고릴라 도판 셋이 at 소제목 바로 뒤에
    await pg.click('.tab[data-s="science"]'); await pg.wait_for_selector("#a-gorilla .infig")
    r = await pg.evaluate("""() => { const a = document.querySelector('#a-gorilla');
      const figs = Array.from(a.querySelectorAll('figure.infig')).map(f => { let p = f.previousElementSibling; while (p && p.tagName === 'FIGURE') p = p.previousElementSibling; return [f.dataset.fig, p ? p.textContent : '']; });
      return figs; }""")
    G = D2["articles"]["gorilla"]["figs"]
    want = [[f["svg"], f["at"]] for f in G if f.get("svg")]
    ok(f"[{name}] 고릴라 도판이 소제목 바로 뒤에(순서대로)", r == want, json.dumps(r, ensure_ascii=False)[:160])
    allfig = await pg.evaluate("""() => Array.from(document.querySelectorAll('figure.infig svg')).filter(s => s.getBoundingClientRect().width > 0).map(s => Math.round(s.getBoundingClientRect().right))""")
    ok(f"[{name}] 과학 도판이 화면 폭 안", all(x <= vp["width"] for x in allfig), f"{len(allfig)}장, 최대 오른쪽 {max(allfig) if allfig else 0}px")
    await pg.evaluate("document.querySelector('#a-gorilla figure.infig').scrollIntoView({block:'start'}); window.scrollBy(0, -70)"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_final_gorilla_fig.png"))
    vis = await pg.evaluate("""() => { const f = document.querySelector('figure[data-fig="n2_merger_s5"]'); if (!f) return null;
      return [getComputedStyle(f.querySelector('.fv')).display, getComputedStyle(f.querySelector('.fh')).display]; }""")
    want_v = ["block", "none"] if vp["width"] < 700 else ["none", "block"]
    ok(f"[{name}] 별 연표: 휴대폰 세로판·PC 가로판", vis == want_v, str(vis))
    # 경제 알림
    await pg.click('.tab[data-s="economy"]'); await pg.wait_for_selector("#a-economy")
    an = await pg.query_selector("#a-economy .anote"); nf = await pg.eval_on_selector_all("#a-economy figure.infig, #a-export figure.infig", "es => es.length")
    ok(f"[{name}] 경제: 꾸민 대화 알림·도판", bool(an) and nf == 3, f"도판 {nf}")
    # 책
    await pg.click('.tab[data-s="lit"]'); await pg.wait_for_selector(".bmethod")
    t = await pg.inner_text("#a-books")
    ok(f"[{name}] 책: 어떻게 골랐나요·『샬롯』 덧말·리뷰+한줄평", "어떻게 골랐나요?" in t and "2000년 판" in t and "리뷰+한줄평" in t and "2026년 11월 19일 조사" in t)
    # 만화
    await pg.click('.tab[data-s="comic"]'); await pg.wait_for_selector(".pnl.ov img")
    await pg.evaluate("Promise.all(Array.from(document.querySelectorAll('.pnl.ov img')).map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))")
    res = await pg.evaluate("""(P) => Array.from(document.querySelectorAll('.pnl.ov')).map((pn, i) => {
      const im = pn.querySelector('.pimg').getBoundingClientRect(); const out = [];
      pn.querySelectorAll('.pimg .bub').forEach(b => { const r = b.getBoundingClientRect();
        const x0 = (r.left - im.left) / im.width * 100, y0 = (r.top - im.top) / im.height * 100, x1 = (r.right - im.left) / im.width * 100, y1 = (r.bottom - im.top) / im.height * 100;
        for (const q of (P[i+1] || [])) if (x0 < q[2] && x1 > q[0] && y0 < q[3] && y1 > q[1]) out.push([i+1, b.textContent, q]);
        if (x1 > 100.5 || y1 > 100.5 || x0 < -0.5) out.push([i+1, b.textContent, '칸 밖']); });
      return [pn.querySelector('img').naturalWidth > 0, out]; })""", {str(k): v for k, v in PROTECT.items()})
    n_ok = sum(1 for x in res if x[0]); hits = [h for x in res for h in x[1]]
    band = await pg.inner_text(".pnl.ov .capband")
    ok(f"[{name}] 만화 7칸 그림·대사가 감과 까마귀를 가리지 않음", n_ok == 7 and not hits, json.dumps(hits, ensure_ascii=False)[:200])
    ok(f"[{name}] 만화 1칸 해설은 아래 띠", "감나무에 감이 딱 하나" in band, band[:30])
    await pg.evaluate("document.querySelector('.strip.ovs').scrollIntoView({block:'start'}); window.scrollBy(0, -60)"); await pg.wait_for_timeout(200)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_final_comic.png"))
    el = await pg.query_selector(".strip.ovs"); await el.screenshot(path=os.path.join(SHOT, f"{name}_final_comic_all.png"))
    # 심리검사 동점
    await pg.click('.tab[data-s="mind"]'); await pg.wait_for_selector("#psyDone")
    Q = D2["articles"]["psytest"]["questions"]
    for i in range(len(Q)):
        await pg.click(f'.psy[data-q="{i}"][data-t="{"A" if i < len(Q)//2 else "B"}"]')
    await pg.click("#psyDone"); n_res = await pg.eval_on_selector_all("#psyRes .result", "es => es.length"); t = await pg.inner_text("#psyRes")
    ico = await pg.eval_on_selector_all("#psyRes .psyico svg", "es => es.length")
    ok(f"[{name}] 심리검사 동점이면 두 유형 다", n_res == 2 and "둘 다 읽어 보세요" in t and ico == 2, f"결과 {n_res}개, 기호 {ico}")
    await pg.evaluate("document.querySelector('#psyRes').scrollIntoView({block:'start'}); window.scrollBy(0, -60)"); await pg.wait_for_timeout(150)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_final_psy_result.png"))
    # 스도쿠 규칙, 영상 안내
    await pg.click('.tab[data-s="sudoku"]'); await pg.wait_for_selector("#sgrid-0")
    t = await pg.inner_text("article.art")
    ok(f"[{name}] 스도쿠 intro·규칙 세 줄", "처음이라면" in t and t.count("1부터 9까지가 한 번씩") >= 3)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_final_sudoku.png"))
    tabs = await pg.eval_on_selector_all(".tab", "es => es.map(e => e.dataset.s)")
    ok(f"[{name}] 제2호: 영상 탭 없음, 사회 탭은 과학 바로 뒤(원고가 있을 때)", "video" not in tabs and (("society" not in [x["id"] for x in D2["sections"]]) or tabs[tabs.index("science") + 1] == "society"), ",".join(tabs))
    # 제1호는 데이터대로 영상 탭이 그대로
    await pg.goto(BASE + "?d=2026-11-17#video"); await pg.wait_for_selector(".vrow")
    nv = await pg.eval_on_selector_all(".vrow", "es => es.length")
    ok(f"[{name}] 제1호 영상 탭은 그대로({len(D1['video']['list'])}편)", nv == len(D1["video"]["list"]), str(nv))
    ok(f"[{name}] 최종 화면 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def visible(pg, sel):
    return await pg.evaluate("""(s) => { const e = document.querySelector(s); if (!e) return false; const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0 && r.left >= 0 && r.right <= innerWidth + 1 && r.top >= 0 && r.bottom <= innerHeight; }""", sel)

async def test_past(br, vp, name):
    """지난 호 보기: 표지·차례·제호 단추, 호 목록(표지 제목·지금 보는 호), 지난 호 띠, 최신 호로 돌아가기, 호마다 따로 기억, 공개 전 호 숨김"""
    ctx, pg, errs = await new_page(br, vp)
    await pg.goto(BASE); await pg.wait_for_selector(".c-foot")
    a = await visible(pg, ".c-foot [data-past]"); b = await visible(pg, ".c-top .c-past"); bar = await pg.query_selector("#pastBar")
    ok(f"[{name}] 표지에 '지난 호 보기' 단추 둘(위·아래)·최신 호라 띠 없음", a and b and not bar, f"아래 {a}, 위 {b}")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_past_cover.png"))
    await pg.click(".c-foot [data-past]"); await pg.wait_for_selector("#modal.on .past-row")
    rows = await pg.eval_on_selector_all("#modal .past-row", "es => es.map(e => [e.dataset.d, e.querySelector('.pr-t').textContent, e.classList.contains('cur')])")
    want = sorted([[x["date"], x["title"], x["date"] == "2026-11-20"] for x in IDX["issues"]], reverse=True)
    ok(f"[{name}] 지난 호 창: 호마다 한 줄(표지 제목, 지금 보는 호 표시)", rows == want, json.dumps(rows, ensure_ascii=False)[:120])
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_past_modal.png"))
    await pg.click("#cc")
    await pg.click('.tab[data-s="science"]'); await pg.wait_for_timeout(200); await pg.evaluate("window.scrollTo(0,0)")
    ok(f"[{name}] 안쪽 쪽에서도 제호 '지난 호 보기' 단추가 보임", await visible(pg, "#calBtn"), await pg.inner_text("#calBtn"))
    await pg.click('.tab[data-s="contents"]'); await pg.wait_for_selector("#pastBox .past-row")
    n = await pg.eval_on_selector_all("#pastBox .past-row", "es => es.length"); cur = await pg.eval_on_selector("#pastBox .past-row.cur", "e => e.dataset.d + ' ' + e.textContent")
    ok(f"[{name}] 차례에 '지난 호 보기' 칸", n == 2 and cur.startswith("2026-11-20") and "지금 보는 호" in cur, cur[:60])
    await pg.evaluate("document.querySelector('#pastBox').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_past_contents.png"))
    await pg.click('#pastBox .past-row[data-d="2026-11-17"]'); await pg.wait_for_selector("#pastBar")
    t = await pg.inner_text("#pastBar"); lab = await pg.inner_text(".c-top b")
    ok(f"[{name}] 지난 호로 가면 띠: '지금 제1호(2026년 11월 17일)를 보고 있어요 · 최신 호 보기'", "?d=2026-11-17" in pg.url and "지금 제1호(2026년 11월 17일)를 보고 있어요" in t and "최신 호 보기" in t and "제1호" in lab, t.replace("\n", " "))
    ov = await overflow(pg); ok(f"[{name}] 띠가 있어도 가로 넘침 없음", ov <= 1, f"{ov}px")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_past_banner_issue1.png"))
    await pg.click("#latestLink"); await pg.wait_for_selector(".c-foot")
    bar = await pg.query_selector("#pastBar"); lab = await pg.inner_text(".c-top b")
    ok(f"[{name}] '최신 호 보기' → ?d 없는 처음 주소, 띠 없음", "?d=" not in pg.url and not bar and "제2호" in lab, pg.url)
    # 호마다 따로 기억(같은 기사 id 'economy'가 두 호에 있음)
    await pg.evaluate("""() => { const S = JSON.parse(localStorage.getItem('nova-1') || '{}'); S.read = Object.assign(S.read || {}, {'2026-11-20:economy': Date.now()});
      S.crown = Object.assign(S.crown || {}, {'2026-11-20:0': Date.now()}); localStorage.setItem('nova-1', JSON.stringify(S)); }""")
    await pg.goto(BASE + "?d=2026-11-17#economy"); await pg.wait_for_selector("#a-economy")
    on1 = await pg.eval_on_selector("#a-economy .rstamp", "e => e.classList.contains('on')")
    await pg.click('.tab[data-s="sudoku"]'); await pg.wait_for_selector("#sgrid-0"); cr1 = await pg.eval_on_selector_all(".crown:not(.ghost)", "es => es.length")
    await pg.goto(BASE + "#economy"); await pg.wait_for_selector("#a-economy")
    on2 = await pg.eval_on_selector("#a-economy .rstamp", "e => e.classList.contains('on')")
    await pg.click('.tab[data-s="sudoku"]'); await pg.wait_for_selector("#sgrid-0"); cr2 = await pg.eval_on_selector("#crown-0", "e => !e.classList.contains('ghost')")
    ok(f"[{name}] 도장·왕관은 호마다 따로(제2호 기록이 제1호에 안 보임)", (not on1) and cr1 == 0 and on2 and cr2, f"제1호 도장 {on1}, 왕관 {cr1} / 제2호 도장 {on2}, 왕관 {cr2}")
    ok(f"[{name}] 지난 호 시험 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()
    # 공개 전 호는 목록에 없음 + title이 없는 호도 깨지지 않음
    fut = json.loads(json.dumps(IDX))
    for x in fut["issues"]:
        if x["date"] == "2026-11-20": x["publishAt"] = "2099-01-01T22:00:00+09:00"
        x.pop("title", None)
    ctx, pg, errs = await new_page(br, vp, idx=fut)
    await pg.goto(BASE + "#contents"); await pg.wait_for_selector("#pastBox")
    rows = await pg.eval_on_selector_all("#pastBox .past-row", "es => es.map(e => e.dataset.d + '|' + e.querySelector('.pr-t').textContent)")
    bar = await pg.query_selector("#pastBar"); lab = await pg.inner_text(".dateline b")
    ok(f"[{name}] 공개 시각 전 호는 목록에 없음·title 없어도 그 호 표지 제목", rows == ["2026-11-17|" + D1["cover"]["headline"]] and not bar and "제1호" in lab, json.dumps(rows, ensure_ascii=False)[:100])
    await pg.goto(BASE + "?d=2026-11-20"); await pg.wait_for_selector(".tab")
    lab = await pg.inner_text(".dateline b")
    ok(f"[{name}] 공개 전 호는 ?d로도 열리지 않음(최신 공개 호로)", "제1호" in lab, lab)
    ok(f"[{name}] 공개 전 시험 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

async def test_society(br, vp, name):
    """제2호 사회 탭: 두 기사(있는 만큼), 국문 요약 단추, 다 읽음 도장, 가로 넘침, 콘솔 오류. 원고가 없으면 탭이 없어야 함"""
    sec = next((x for x in D2["sections"] if x["id"] == "society"), None)
    ids = [i for i in ["society_a", "society_b"] if i in D2["articles"]]
    ctx, pg, errs = await new_page(br, vp, clock=True)
    await pg.goto(BASE + "#contents"); await pg.wait_for_selector(".tab")
    if not ids:
        has = await pg.query_selector('.tab[data-s="society"]')
        ok(f"[{name}] 사회 원고가 없으면 사회 탭 없이 조립", sec is None and not has); await ctx.close(); return
    await pg.click('.tab[data-s="society"]'); await pg.wait_for_selector("article.art")
    got = await pg.eval_on_selector_all("article.art", "es => es.map(e => e.id.replace('a-', ''))")
    ok(f"[{name}] 사회 탭 기사 {len(ids)}편 열림", got == ids and sec["en"] == "SOCIETY" and sec["desc"] == "이번 주 세상 이야기", ",".join(got))
    for i in ids:
        en = sum(1 for x in D2["articles"][i].get("sources", []) if x.get("lang") == "en" and x.get("ko"))
        nb = await pg.eval_on_selector_all(f"#a-{i} .kbtn", "es => es.length")
        if nb:
            await pg.click(f"#a-{i} .kbtn >> nth=0"); shown = await pg.eval_on_selector(f"#a-{i} .ko", "e => e.classList.contains('on')")
        else: shown = True
        ok(f"[{name}] {i} 국문 요약 단추(영어 출처 {en}개)", nb == en and shown, f"단추 {nb}개" + ("" if en else " · 이 기사 출처는 모두 한국어"))
    toc = await pg.evaluate("() => 1")
    i = ids[0]
    need = await pg.eval_on_selector(f"#a-{i}", "e => +e.dataset.need")
    await pg.evaluate(f"window.scrollTo(0, document.querySelector('#a-{i}').offsetTop)")
    await pg.clock.run_for(need * 1000 + 500)
    await pg.evaluate(f"document.querySelector('#a-{i} .endmark').scrollIntoView({{block:'center'}})"); await pg.wait_for_timeout(150)
    await pg.clock.run_for(1000); await pg.wait_for_timeout(200)
    on = await pg.eval_on_selector(f"#a-{i} .rstamp", "e => e.classList.contains('on')")
    ok(f"[{name}] 사회 기사 다 읽음 도장", on)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_society_stamp.png"))
    await pg.click('.tab[data-s="contents"]'); await pg.wait_for_timeout(200)
    rows = await pg.eval_on_selector_all(".toc-row", "es => es.filter(r => r.dataset.go === 'society').map(r => !!r.querySelector('.tread'))")
    ok(f"[{name}] 차례에 사회 기사 줄·읽음 표시", len(rows) == len(ids) and rows[0], str(rows))
    await pg.click('.tab[data-s="society"]'); await pg.wait_for_timeout(200); await pg.evaluate("window.scrollTo(0,0)")
    ov = await overflow(pg); ok(f"[{name}] 사회 탭 가로 넘침 없음", ov <= 1, f"{ov}px")
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_society_top.png"))
    nq = sum(1 for lv in D2["newsQuiz"].values() for q in lv if q.get("from") in ids)
    cl = [l for l in D2["cover"]["lines"] if l.get("go") == "society"]
    ok(f"[{name}] 사회 기사가 뉴스 퀴즈 풀·표지 목록에", nq >= 3 and len(cl) >= 1, f"퀴즈 {nq}문제, 표지 줄 {len(cl)}")
    ok(f"[{name}] 사회 탭 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()

def server_ratings():
    import urllib.request
    with urllib.request.urlopen(f"http://127.0.0.1:{ASKPORT}/ask/ratings", timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))["ratings"]

async def star(pg, sel, n):
    await pg.click(f'{sel} .star[data-v="{n}"]')

async def test_rating(br, vp, name):
    """기사 별점: 다른 기기(이 기기에만 저장), 서아 기기(등록 실패·성공, 전송, 다시 누르면 바뀜), 준비 안 됨, 전송 실패, 두 호"""
    ASK = f"http://127.0.0.1:{ASKPORT}/ask"
    G = '.rate[data-rid2="gorilla"]'
    # (가) 친구 기기: 처음 누르면 확인 창 → '그냥 이 기기에만 저장'
    before = server_ratings()
    ctx, pg, errs = await new_page(br, vp, ask_url=ASK)
    await pg.goto(BASE + "#science"); await pg.wait_for_selector(G)
    await pg.evaluate(f"document.querySelector('{G}').scrollIntoView({{block:'center'}})")
    await star(pg, G, 3); await pg.wait_for_selector("#modal.on #seoaCode")
    t = await pg.inner_text("#sheet")
    ok(f"[{name}] 별을 처음 누르면 서아 확인 창", "서아만 Nova에 별점을 보낼 수 있어요" in t and "처음 한 번만" in t)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_rate_modal.png"))
    await pg.click("#seoaLocal"); await pg.wait_for_timeout(150)
    on = await pg.eval_on_selector_all(f"{G} .star.on", "es => es.length"); rs = await pg.inner_text(f"{G} .rs")
    await star(pg, '.rate[data-rid2="merger"]', 5); await pg.wait_for_timeout(150)
    again = await pg.query_selector("#modal.on")
    ok(f"[{name}] 이 기기에만 저장: 별 칠해짐·다시 묻지 않음", on == 3 and "이 기기에 ★3" in rs and not again, rs)
    await pg.reload(); await pg.wait_for_selector(G)
    on = await pg.eval_on_selector_all(f"{G} .star.on", "es => es.length"); badge = await pg.query_selector(".seoa-b")
    srv = server_ratings()
    ok(f"[{name}] 친구 기기 별점은 기기에만(새로 고침 뒤 남음, 서버에 안 감, 서아 표시 없음)", on == 3 and not badge and srv == before, "서버 그대로" if srv == before else json.dumps(srv, ensure_ascii=False)[:80])
    ok(f"[{name}] 친구 기기 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()
    # (나) 서아 기기: 틀린 암호 → 맞는 암호 → 전송, 다시 누르면 바뀜
    ctx, pg, errs = await new_page(br, vp, ask_url=ASK)
    await pg.goto(BASE + "#science"); await pg.wait_for_selector(G)
    await pg.evaluate(f"document.querySelector('{G}').scrollIntoView({{block:'center'}})")
    await star(pg, G, 4); await pg.wait_for_selector("#modal.on #seoaCode")
    await pg.fill("#seoaCode", "틀린암호"); await pg.click("#seoaOk"); await pg.wait_for_function("document.querySelector('#seoaMsg').textContent.includes('맞지')")
    m = await pg.inner_text("#seoaMsg")
    ok(f"[{name}] 틀린 암호 → '암호가 맞지 않아요'", "암호가 맞지 않아요" in m, m)
    await pg.fill("#seoaCode", SEOA_CODE); await pg.click("#seoaOk")
    await pg.wait_for_function("!document.querySelector('#modal.on')")
    await pg.wait_for_function("document.querySelector('.rate[data-rid2=\"gorilla\"] .rs').textContent.includes('보냈어요')")
    rs = await pg.inner_text(f"{G} .rs"); badge = await pg.inner_text("#a-gorilla > .title .seoa-b")
    tok = await pg.evaluate("JSON.parse(localStorage.getItem('nova-1')).seoa")
    srv = server_ratings()
    ok(f"[{name}] 맞는 암호 → 서아 기기 등록·별점 전송·제목 옆 '서아 별점 ★4'", tok.get("mode") == "seoa" and len(tok.get("token", "")) >= 32 and srv["2026-11-20"]["gorilla"]["stars"] == 4 and "★4" in badge, rs)
    await pg.screenshot(path=os.path.join(SHOT, f"{name}_rate_article_end.png"))
    await star(pg, G, 2); await pg.wait_for_function("document.querySelector('.rate[data-rid2=\"gorilla\"] .rs').textContent.includes('★2') && document.querySelector('.rate[data-rid2=\"gorilla\"] .rs').textContent.includes('보냈어요')")
    srv = server_ratings(); badge = await pg.inner_text("#a-gorilla > .title .seoa-b")
    ok(f"[{name}] 다시 누르면 새 값(★2)으로 바뀜", srv["2026-11-20"]["gorilla"]["stars"] == 2 and "★2" in badge)
    # 책(책마다)·만화·사회
    await pg.click('.tab[data-s="lit"]'); await pg.wait_for_selector(".book .rate")
    bid = await pg.eval_on_selector(".book .rate", "e => e.dataset.rid2")
    await star(pg, f'.rate[data-rid2="{bid}"]', 5); await pg.wait_for_function(f"document.querySelector('.rate[data-rid2=\"{bid}\"] .rs').textContent.includes('보냈어요')")
    nb = await pg.eval_on_selector_all(".book .rate", "es => es.length")
    await pg.click('.tab[data-s="comic"]'); await pg.wait_for_selector('.rate[data-rid2="comic"]')
    await star(pg, '.rate[data-rid2="comic"]', 4); await pg.wait_for_function("document.querySelector('.rate[data-rid2=\"comic\"] .rs').textContent.includes('보냈어요')")
    srv = server_ratings()["2026-11-20"]
    ok(f"[{name}] 책마다·만화 별점 전송", nb == 3 and srv.get(bid, {}).get("stars") == 5 and srv.get("comic", {}).get("stars") == 4, f"책 칸 {nb}, {bid}")
    secs = {"society": ["society_a", "society_b"], "math": ["folding", "snowflake"], "economy": ["economy", "export"], "art": ["art", "art2"], "mind": ["purr"]}
    miss = []
    for sid, ids in secs.items():
        if not any(x["id"] == sid for x in D2["sections"]): continue
        await pg.click(f'.tab[data-s="{sid}"]'); await pg.wait_for_timeout(150)
        for i in ids:
            if i in D2["articles"] and not await pg.query_selector(f'.rate[data-rid2="{i}"]'): miss.append(i)
    nopsy = not await pg.query_selector('.rate[data-rid2="psytest"]')
    ok(f"[{name}] 사회·수학·경제·예술·심리 기사마다 별점 칸", not miss and nopsy, f"없음: {miss}")
    await pg.click('.tab[data-s="contents"]'); await pg.wait_for_selector(".toc-row")
    tb = await pg.eval_on_selector_all(".toc-row .seoa-b", "es => es.map(e => e.textContent)"); ss = await pg.inner_text("#seoaSet")
    ok(f"[{name}] 서아 기기 차례에 '서아 별점' 표시·설정 칸", "서아 별점 ★2" in tb and "서아 기기" in ss, json.dumps(tb, ensure_ascii=False))
    # 지난 호(제1호)도 별점 칸이 있고 호마다 따로 저장
    await pg.goto(BASE + "?d=2026-11-17#science"); await pg.wait_for_selector('.rate[data-rid2="voyager"]')
    on1 = await pg.query_selector_all('.rate .star.on')
    await star(pg, '.rate[data-rid2="voyager"]', 5); await pg.wait_for_function("document.querySelector('.rate[data-rid2=\"voyager\"] .rs').textContent.includes('보냈어요')")
    srv = server_ratings()
    ok(f"[{name}] 제1호에서도 별점(호마다 따로)", not on1 and srv["2026-11-17"]["voyager"]["stars"] == 5, "")
    # 보내기 실패해도 화면은 멀쩡
    await pg.route(f"http://127.0.0.1:{ASKPORT}/ask/rate", lambda r: r.abort())
    await star(pg, '.rate[data-rid2="voyager"]', 3); await pg.wait_for_function("document.querySelector('.rate[data-rid2=\"voyager\"] .rs').textContent.includes('못 보냈어요')")
    on = await pg.eval_on_selector_all('.rate[data-rid2="voyager"] .star.on', "es => es.length")
    ok(f"[{name}] 전송 실패해도 별은 기기에 남음", on == 3)
    ok(f"[{name}] 서아 기기 콘솔 오류 없음", not errs, "; ".join(errs[:3]))
    await ctx.close()
    # (다) 서버에 암호가 아직 없을 때
    ctx, pg, errs = await new_page(br, vp, ask_url=ASK)
    async def nr(route): await route.fulfill(status=503, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}, body='{"error":"not_ready"}')
    await pg.route(f"http://127.0.0.1:{ASKPORT}/ask/seoa/register", nr)
    await pg.goto(BASE + "#science"); await pg.wait_for_selector(G)
    await star(pg, G, 5); await pg.wait_for_selector("#modal.on #seoaCode")
    await pg.fill("#seoaCode", "아무거나"); await pg.click("#seoaOk")
    await pg.wait_for_function("document.querySelector('#seoaMsg') && document.querySelector('#seoaMsg').textContent.includes('준비 중')")
    m = await pg.inner_text("#seoaMsg"); await pg.wait_for_timeout(1900)
    closed = not await pg.query_selector("#modal.on"); on = await pg.eval_on_selector_all(f"{G} .star.on", "es => es.length")
    ok(f"[{name}] 서버 준비 전: '아직 준비 중이에요. 이 기기에만 저장할게요'", "아직 준비 중이에요. 이 기기에만 저장할게요" in m and closed and on == 5, m)
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
    shutil.rmtree(ASKDATA, ignore_errors=True)
    env = dict(os.environ, NOVA_FAKE="1", NOVA_ALLOW_LOCAL="1", NOVA_PORT=str(ASKPORT), NOVA_SEOA_CODE=SEOA_CODE, NOVA_DATA_DIR=ASKDATA); env.pop("ANTHROPIC_API_KEY", None)
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
                await test_final(br, vp, name)
                await test_past(br, vp, name)
                await test_society(br, vp, name)
                await test_rating(br, vp, name)
            await test_figimg(br)
            await test_inline(br)
            await br.close()
    finally:
        web.terminate(); ask.terminate()
    bad = [r for r in RESULTS if not r[1]]
    print(f"\n결과: {len(RESULTS) - len(bad)} / {len(RESULTS)} 통과" + ("" if not bad else "\n실패: " + "\n  ".join(f"{n} | {d}" for n, _, d in bad)))
    sys.exit(1 if bad else 0)

asyncio.run(main())
