import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, vp in [("phone", {"width":390,"height":844}), ("pc", {"width":1280,"height":900})]:
            pg = await b.new_page(viewport=vp)
            errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("file:///home/claude/seoa/build/out3/index.html"); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f"/tmp/s3_{name}_cover.png")
            sh = await pg.evaluate("[document.documentElement.scrollHeight, window.innerHeight]")
            print(name, "표지 높이(문서, 창):", sh)
            await pg.evaluate("""(()=>{const k=window.__INLINE__.articles.kakeya; if(!k.body.some(b=>b.t==='sim')) k.body.splice(2,0,{t:'sim',x:'kakeya'});})()""")
            await pg.evaluate("document.querySelector('.tab[data-s=math]').click()"); await pg.wait_for_timeout(500)
            await pg.click("#simPlay"); await pg.wait_for_timeout(6800)
            c = await pg.inner_text("#simC")
            await pg.click(".sim-modes button[data-m=d]"); await pg.click("#simPlay"); await pg.wait_for_timeout(3000)
            el = await pg.query_selector("#sim"); await el.screenshot(path=f"/tmp/s3_{name}_sim_mid.png")
            await pg.wait_for_timeout(3800)
            d = await pg.inner_text("#simD"); note = await pg.inner_text("#simNote")
            await el.screenshot(path=f"/tmp/s3_{name}_sim.png")
            print(name, "동그라미:", c, "| 별:", d, "| 안내:", note[:60], "| 오류:", errs or "없음")
            await pg.evaluate("document.querySelector('.tab[data-s=contents]').click()"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f"/tmp/s3_{name}_contents.png")
            # 낱말 풀이
            await pg.evaluate("document.querySelector('.tab[data-s=science]').click()"); await pg.wait_for_timeout(300)
            n = await pg.evaluate("document.querySelectorAll('.tw').length")
            if n:
                await pg.click(".tw >> nth=0"); await pg.wait_for_timeout(200)
                print(name, "낱말 수:", n, "| 풀이:", (await pg.inner_text("#tip"))[:50])
        await b.close()
asyncio.run(main())
