import asyncio, sys
from playwright.async_api import async_playwright
SECS = ["cover","science","math","economy","art","lit","mind","comic","sudoku","quiz","video","chiikawa"]
async def main(which):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, vp in [("phone", {"width":390,"height":844}), ("pc", {"width":1280,"height":900})]:
            pg = await b.new_page(viewport=vp, device_scale_factor=1 if name=="pc" else 2)
            errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("file:///home/claude/seoa/build/out3/index.html"); await pg.wait_for_timeout(1500)
            for s in which:
                await pg.evaluate(f"document.querySelector('.tab[data-s={s}]').click()"); await pg.wait_for_timeout(400)
                await pg.screenshot(path=f"v3_{name}_{s}.png", full_page=False)
            # 가로 넘침 검사
            ov = await pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
            print(name, "가로 넘침:", ov, "| 오류:", errs or "없음")
            await pg.close()
        await b.close()
asyncio.run(main(sys.argv[1:] or SECS))
