# 제1호 개편 원고 형식 (기자용)

반드시 /home/claude/seoa/build/drafts/README_잡지기준.md 를 먼저 읽고 문체·길이 기준을 따른다.
공통: 한국어로만. 사용자 컴퓨터 도구(mcp__remote-devices 로 시작) 사용 금지. 출처는 프롬프트에 적힌 URL과 /home/claude/seoa/build/src/*.txt 에 저장된 본문을 쓴다.
웹 페이지를 더 열어야 하면 WebFetch 대신 Bash로 curl -sL -A "Mozilla/5.0" URL 을 써서 읽는다(승인 대기 방지). 원문 문장을 옮기지 말고 자기 말로 쓴다. 직접 인용 금지.

## 기사 파일(JSON, 경로는 /home/claude/seoa/build/v2/<id>.json)
{
 "id": "영문 소문자",
 "section": "과학" | "수학" | "경제" | "예술" | "심리",
 "kicker": "과학 뉴스" | "특집" | "깊이 읽기" | "이번 주 밤하늘" | "또래 연구자" 등,
 "title": "신문식 제목",
 "deck": "기사 전체를 한 문장으로",
 "body": [
   {"t":"p","x":"문단"},
   {"t":"h","x":"소제목"},
   {"t":"box","title":"한눈에 보기 / 더 알아보기 / 직접 해 보기","x":"내용", "items":["(선택) 목록"]},
   {"t":"quote","x":"본문 가운데 크게 뽑을 한 문장(자기 말로, 따옴표 없이)"}
 ],
 "terms": [{"w":"용어","m":"풀이"}],            // 용어 정리 3~5개
 "figs": [{"cap":"그림 설명 한 문장","brief":"도판 설명: 무엇을 어떤 도식으로(선화+빨강/남색, 라벨 허용)"}],   // 1~2개
 "sources": [{"t":"원문 제목 그대로","pub":"매체·기관","date":"YYYY-MM-DD","u":"URL","lang":"ko|en"}],
 "facts": [{"claim":"숫자·이름·날짜가 들어간 사실","source":"URL"}],
 "quiz": {"쉬움":[2문제],"보통":[2문제],"어려움":[2문제]}
}
퀴즈 형식: OX {"type":"ox","q","answer":"O|X","explain"} / 객관식 {"type":"mc","q","options":[4개],"answer":0부터,"explain"} / 주관식 {"type":"short","q","answer","accept":[...],"explain"}.
퀴즈 원칙: 문제만 따로 봐도 어느 기사인지 알게 쓴다. "어려움"은 이름·연도 외우기가 아니라 "밝혀진 것과 짐작 구분", "까닭 고르기". 주관식 정답은 쉬운 낱말 하나나 간단한 숫자.
다 쓰면 python3 -m json.tool 로 검사한다.
