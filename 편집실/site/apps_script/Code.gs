/**
 * Nova 기록 서버 (Apps Script)
 * 하는 일: 웹앱에서 보낸 좋아요·싫어요, 퀴즈 결과, 스도쿠, 질문을 "서아 페이퍼 데이터베이스(Nova)" 시트에 쌓고,
 *          답이 달린 질문을 웹앱에 돌려준다.
 * 설치: 데이터베이스 시트 > 확장 프로그램 > Apps Script > 이 코드 전체 붙여넣기 > 저장
 *       > 배포 > 새 배포 > 유형: 웹 앱 > 실행: 나 / 액세스 권한: 모든 사용자 > 배포 > 웹 앱 URL 복사
 * (선택) 질문에 바로 답하기: 프로젝트 설정 > 스크립트 속성 > ANTHROPIC_API_KEY 추가.
 *        넣지 않으면 질문은 시트 "질문" 탭에 쌓이고, 답 칸이 채워지면 웹앱에 보인다.
 */
const ASK_PROMPT = `너는 과학 교양지 'Nova'의 선생님이야. 질문한 사람은 초등학교 4학년 서아야. 다음을 꼭 지켜.
1) 4학년이 이해할 수 있는 쉬운 말로, '~해요'체로 3~6문장으로 답해.
2) 정확하게 답해. 확실하지 않으면 '아직 과학자들도 정확히 모른대요'나 '선생님도 확실하지 않아요'처럼 솔직하게 말해. 지어내지 마.
3) 이해를 돕는 쉬운 예를 하나 들어.
4) 마지막 줄에 더 생각해 볼 질문을 하나 던져.
5) 다치거나 아픈 일, 위험한 실험, 무서운 이야기, 친구와 다툼처럼 어른의 도움이 필요한 질문은 부드럽게 답하고 엄마 아빠나 선생님과 꼭 이야기해 보라고 권해.
6) 숙제 답을 통째로 대신 써 주지 말고, 스스로 풀 수 있게 힌트를 줘.
7) 이름, 주소, 학교 같은 개인정보는 묻지도 적지도 마.
8) 마크다운 기호(#, *, -)는 쓰지 말고 그냥 문장으로 써.`;
const MODEL = 'claude-sonnet-5-5';

function sheet_(name, headers) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(headers); sh.setFrozenRows(1); }
  return sh;
}
const QUIZ_HEAD = ['시각', '날짜', '종류(수학/뉴스)', '난이도', '맞힌 수', '받은 코인', '탭 열림'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const d = JSON.parse((e.postData && e.postData.contents) || '{}');
    const t = d.t ? new Date(d.t) : new Date();
    if (d.kind === 'reaction') {
      sheet_('반응 기록', ['시각', '호수', '대상 종류(기사/영상)', '대상ID', '반응(좋아요/싫어요)'])
        .appendRow([t, d.issue, d.target, d.id, d.r === 'like' ? '좋아요' : d.r === 'dislike' ? '싫어요' : (d.r || '')]);
    } else if (d.kind === 'quiz') {
      sheet_('퀴즈 기록', QUIZ_HEAD).appendRow([t, d.date, d.type, d.level, d.score, d.coins, d.unlocked ? '열림' : '']);
    } else if (d.kind === 'sudoku') {
      sheet_('퀴즈 기록', QUIZ_HEAD).appendRow([t, d.date, '스도쿠', '', '', d.coins, '']);
    } else if (d.kind === 'question') {
      const q = String(d.q || '').slice(0, 500);
      let a = d.a || '';
      if (!a) a = answer_(q);
      sheet_('질문', ['시각', '호수', '질문', '답', '답한 시각']).appendRow([t, d.issue, q, a, a ? new Date() : '']);
    }
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}

function answer_(q) {
  const key = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  if (!key || !q) return '';
  try {
    const res = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01' },
      payload: JSON.stringify({ model: MODEL, max_tokens: 700, system: ASK_PROMPT, messages: [{ role: 'user', content: q }] })
    });
    const j = JSON.parse(res.getContentText());
    return (j.content && j.content[0] && j.content[0].text) || '';
  } catch (err) {
    return '';
  }
}

function doGet(e) {
  if (e.parameter.action === 'answers') {
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('질문');
    const out = [];
    if (sh && sh.getLastRow() > 1) {
      sh.getRange(2, 1, sh.getLastRow() - 1, 5).getValues().forEach(function (r) {
        if (r[3]) out.push({ q: r[2], a: r[3] });
      });
    }
    return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
  }
  return ContentService.createTextOutput('Nova 기록 서버가 켜져 있어요.');
}
