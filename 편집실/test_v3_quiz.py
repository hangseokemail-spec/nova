import asyncio, json, re
from playwright.async_api import async_playwright
data = json.load(open("out3/data.json"))
async def run(pg, typ, lv):
    await pg.evaluate("document.querySelector('.tab[data-s=quiz]').click()"); await pg.wait_for_timeout(150)
    await pg.click(f"[data-type={typ}]"); await pg.click(f"[data-l={lv}]")
    qs = data["mathQuiz" if typ=="math" else "newsQuiz"][lv]
    for q in qs:
        if q["type"]=="ox": await pg.click(f"#quizBox [data-a={q['answer']}]")
        elif q["type"]=="mc": await pg.click(f"#quizBox .opt[data-a='{q['answer']}']")
        elif typ=="math":
            for ch in q["answer"]: await pg.click(f"[data-k='{ch}']")
            await pg.click("[data-k=확인]")
        else:
            await pg.fill("#tin", q["answer"]); await pg.click("#tok")
        await pg.click("#nx")
    t = await pg.inner_text("#quizBox"); m = re.search(r"(\d+) / (\d+)", t)
    return m.group(0) if m else t[:80]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":390,"height":844})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/claude/seoa/build/out3/index.html"); await pg.wait_for_timeout(800)
        for typ in ["news","math"]:
            for lv in ["쉬움","보통","어려움"]: print(typ, lv, await run(pg, typ, lv))
        # 심리검사 끝까지
        await pg.evaluate("document.querySelector('.tab[data-s=mind]').click()"); await pg.wait_for_timeout(200)
        n = await pg.evaluate("document.querySelectorAll('.psy').length")
        qn = len(data["articles"]["psytest"]["questions"])
        for i in range(qn): await pg.click(f".psy[data-q='{i}']")
        await pg.click("#psyDone"); await pg.wait_for_timeout(200)
        print("심리검사 결과:", (await pg.inner_text("#psyRes"))[:60].replace("\n"," "))
        # 국문 요약 버튼
        await pg.evaluate("document.querySelector('.tab[data-s=science]').click()"); await pg.wait_for_timeout(200)
        kb = await pg.evaluate("document.querySelectorAll('.kbtn').length")
        print("과학 쪽 국문 요약 버튼:", kb)
        print("오류:", errs or "없음")
        await b.close()
asyncio.run(main())
