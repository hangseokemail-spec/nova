#!/usr/bin/env bash
# Nova 질문 서버 한 번에 설치 (AWS Lightsail 우분투, 브라우저 SSH 창에 한 줄만 붙여 넣기)
#   curl -fsSL <이 파일 주소> -o /tmp/nova_setup.sh && sudo bash /tmp/nova_setup.sh
# 하는 일: 보안 업데이트 → 서버 파일 받기 → 설치(install.sh) → API 키 넣기(또는 시험 모드) → 동작 확인
# API 키는 이 화면에서 편집인이 직접 입력하고, 서버의 /etc/nova-ask.env(권한 600)에만 저장돼요.
set -uo pipefail
B="https://raw.githubusercontent.com/hangseokemail-spec/nova/main/%ED%8E%B8%EC%A7%91%EC%8B%A4/site/ask_server"
SRC=/opt/nova-ask-src
hr() { printf '\n\033[1m==================== %s ====================\033[0m\n' "$*"; }
stop() { printf '\n\033[31m[멈춤] %s\033[0m\n이 화면의 글을 복사해 Claude에게 보내 주세요.\n' "$*"; exit 1; }
[ "$(id -u)" = 0 ] || stop "sudo를 붙여 실행해 주세요: sudo bash /tmp/nova_setup.sh"

hr "1/5 보안 업데이트 (몇 분 걸려요)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold upgrade \
  || echo "(업데이트 중 경고가 있었지만 계속할게요)"

hr "2/5 서버 파일 받기"
install -d -m 755 "$SRC"
for f in nova_ask.py nova-ask.service install.sh; do
  curl -fsSL "$B/$f" -o "$SRC/$f" || stop "파일을 받지 못했어요: $f"
done
ls -l "$SRC"

hr "3/5 설치"
bash "$SRC/install.sh" || stop "설치가 멈췄어요. 위쪽의 [멈춤] 글이 까닭이에요."

hr "4/5 API 키"
echo "Anthropic API 키를 지금 넣을까요?"
echo "  y = 지금 넣기 (질문에 진짜 답이 나와요. 사용한 만큼 요금이 나와요)"
echo "  n = 나중에 넣기 (연결만 시험하는 '시험용 답' 모드로 켜 둬요)"
read -rp "y 또는 n: " ans
case "$ans" in
  y|Y|ㅛ) bash "$SRC/install.sh" set-key || stop "키를 저장하지 못했어요." ;;
  *) bash "$SRC/install.sh" fake on; echo "나중에 키를 넣을 때: sudo bash $SRC/install.sh set-key" ;;
esac

hr "5/5 동작 확인 (인증서를 받는 동안 20초 기다려요)"
sleep 20
bash "$SRC/install.sh" check

hr "끝"
cat <<'EOF'
- 위 3)과 4)에 {"ok": true ...} 와 {"a": "..."} 가 보이면 성공이에요.
- 3)에서 'https로 닿지 않아요'가 나오면: Lightsail 네트워킹 탭에서 HTTP·HTTPS 규칙을 연 뒤
  1~2분 기다렸다가 아래 한 줄로 다시 확인해 주세요.
    sudo bash /opt/nova-ask-src/install.sh check
- 이 화면 맨 아래 부분을 복사해 Claude에게 보내 주시면 사이트에 연결할게요.
  (화면에 API 키는 나오지 않아요.)
EOF
