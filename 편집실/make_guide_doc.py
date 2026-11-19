# 작업 지침서 합본 만들기(드라이브 01_기획·운영에 올릴 문서): python3 편집실/make_guide_doc.py
import os, datetime
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
parts = [("편집 지침 (CLAUDE.md)", os.path.join(R, "CLAUDE.md")),
         ("제작 방식: Opus 기자 4명 + Fable 편집장", os.path.join(B, "drafts", "README_오퍼스4인.md")),
         ("원고 기준 (README_v3)", os.path.join(B, "drafts", "README_v3.md")),
         ("원고 형식 (README_새형식)", os.path.join(B, "drafts", "README_새형식.md")),
         ("문체·길이 기준 (README_잡지기준)", os.path.join(B, "drafts", "README_잡지기준.md"))]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
out = [f"# Nova 작업 지침서 (최신, {now} 한국 시각)\n",
       "정식 원본은 깃허브 저장소 hangseokemail-spec/nova 의 CLAUDE.md와 편집실/drafts/README_*.md 예요. 이 문서는 그 합본 사본이고, 지침이 바뀔 때마다 새로 올려요.\n"]
for title, path in parts:
    txt = open(path, encoding="utf-8").read()
    txt = "\n".join(("#" + l) if l.startswith("#") else l for l in txt.splitlines())
    out.append(f"\n---\n\n# {title}\n\n{txt}\n")
s = "".join(out); s = "".join(c for c in s if ord(c) <= 0xFFFF)   # 드라이브에서 깨지는 4바이트 문자 빼기
dst = os.path.join(B, "drafts", "Nova_작업지침서_합본.md"); open(dst, "w", encoding="utf-8").write(s)
print(dst, len(s), now)
