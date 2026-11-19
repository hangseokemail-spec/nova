#!/usr/bin/env bash
# Nova 질문 서버 설치 (Ubuntu, AWS Lightsail)
#   sudo bash install.sh            설치(서버 프로그램 + 서비스 + 80·443이 비어 있으면 Caddy로 https)
#   sudo bash install.sh set-key    Anthropic API 키 넣기(화면에 보이지 않게 입력)
#   sudo bash install.sh check      동작 확인
#   sudo bash install.sh fake on|off  키 없이 '시험용 답' 모드 켜기/끄기
# 다른 IP를 쓰면: sudo NOVA_IP=1.2.3.4 bash install.sh
set -euo pipefail

NOVA_IP="${NOVA_IP:-3.34.169.45}"
DOMAIN="${NOVA_DOMAIN:-${NOVA_IP//./-}.sslip.io}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVF=/etc/nova-ask.env
APPD=/opt/nova-ask
ORIGIN="https://hangseokemail-spec.github.io"

say()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
die()  { printf '\n\033[31m[멈춤] %s\033[0m\n' "$*" >&2; exit 1; }
need_root() { [ "$(id -u)" = 0 ] || die "sudo를 붙여 실행해 주세요: sudo bash install.sh $*"; }

# 포트를 쓰고 있는 프로그램 이름(없으면 빈 값)
port_owner() { ss -Hltnp "( sport = :$1 )" 2>/dev/null | sed -n 's/.*users:(("\([^"]*\)".*/\1/p' | head -n1; }

set_env() {   # set_env 이름 값  (키가 아닌 일반 설정만)
  local k="$1" v="$2" tmp
  tmp="$(mktemp "$ENVF.XXXX")"; chmod 600 "$tmp"
  grep -v "^$k=" "$ENVF" > "$tmp" || true
  printf '%s=%s\n' "$k" "$v" >> "$tmp"
  mv "$tmp" "$ENVF"; chown root:root "$ENVF"; chmod 600 "$ENVF"
}

cmd_set_key() {
  need_root set-key
  [ -f "$ENVF" ] || die "먼저 설치해 주세요: sudo bash install.sh"
  local K="" tmp line
  read -rsp "Anthropic API 키를 붙여 넣고 Enter를 누르세요(화면에는 보이지 않아요): " K; echo
  K="${K//[[:space:]]/}"
  [ -n "$K" ] || die "키가 비어 있어요. 다시 해 주세요."
  case "$K" in sk-ant-*) ;; *) echo "알림: 보통 Anthropic 키는 sk-ant- 로 시작해요. 그래도 저장할게요.";; esac
  tmp="$(mktemp "$ENVF.XXXX")"; chmod 600 "$tmp"
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ANTHROPIC_API_KEY=*) ;; *) printf '%s\n' "$line" ;; esac
  done < "$ENVF" > "$tmp"
  printf 'ANTHROPIC_API_KEY=%s\n' "$K" >> "$tmp"     # printf는 셸 안에서 처리되어 다른 프로그램 목록에 키가 보이지 않아요
  unset K
  mv "$tmp" "$ENVF"; chown root:root "$ENVF"; chmod 600 "$ENVF"
  set_env NOVA_FAKE 0
  systemctl restart nova-ask
  echo "키를 저장했어요(/etc/nova-ask.env, root만 읽기). 서비스를 다시 켰어요."
}

cmd_fake() {
  need_root fake
  case "${1:-}" in on) set_env NOVA_FAKE 1 ;; off) set_env NOVA_FAKE 0 ;; *) die "sudo bash install.sh fake on  또는  fake off" ;; esac
  systemctl restart nova-ask; echo "시험용 답 모드: ${1}"
}

cmd_check() {
  say "1) 서비스 상태"
  systemctl is-active nova-ask && echo "nova-ask 켜져 있음" || echo "nova-ask 꺼져 있음: sudo journalctl -u nova-ask -n 30"
  say "2) 서버 안쪽(127.0.0.1:8787)"
  curl -s --max-time 5 http://127.0.0.1:8787/ask/health; echo
  say "3) 바깥 https 주소(https://$DOMAIN/ask)"
  curl -s --max-time 15 "https://$DOMAIN/ask/health" || echo "(https로 닿지 않아요. Lightsail 방화벽에서 80·443이 열려 있는지 확인해 주세요)"; echo
  say "4) 질문 한 번 보내 보기"
  curl -s --max-time 60 -X POST "https://$DOMAIN/ask" -H "Origin: $ORIGIN" -H 'Content-Type: text/plain' \
       --data '{"q":"하늘은 왜 파란색이에요?","issue":2}'; echo
}

cmd_install() {
  need_root
  command -v python3 >/dev/null || { apt-get update && apt-get install -y python3; }
  python3 -c 'import sys; assert sys.version_info >= (3, 7)' || die "python3 3.7 이상이 필요해요."
  [ -f "$HERE/nova_ask.py" ] && [ -f "$HERE/nova-ask.service" ] || die "nova_ask.py와 nova-ask.service가 install.sh와 같은 폴더에 있어야 해요."

  say "1) 80·443 포트 확인"
  command -v ss >/dev/null || { apt-get update && apt-get install -y iproute2; }
  local o80 o443 mode
  o80="$(port_owner 80)"; o443="$(port_owner 443)"
  echo "80번: ${o80:-비어 있음} / 443번: ${o443:-비어 있음}"
  mode=""
  for o in "$o80" "$o443"; do
    case "$o" in
      "") ;;
      caddy) mode="caddy-existing" ;;
      nginx*|apache2*|httpd*) die "80·443을 이미 '$o'가 쓰고 있어요. Caddy를 깔지 않고 멈춰요.
README.md의 '이미 nginx나 apache를 쓰고 있다면' 부분의 몇 줄을 그 설정에 넣어 주세요.
(서버 프로그램만 먼저 깔려면: sudo NOVA_NO_HTTPS=1 bash install.sh)" ;;
      *) [ "${NOVA_NO_HTTPS:-0}" = 1 ] || die "80·443을 '$o'가 쓰고 있어요. 무엇인지 확인한 뒤 다시 해 주세요(README 참고)." ;;
    esac
  done
  [ "${NOVA_NO_HTTPS:-0}" = 1 ] && mode="none"

  say "2) 서버 프로그램 설치($APPD)"
  install -d -m 755 "$APPD"
  install -m 644 "$HERE/nova_ask.py" "$APPD/nova_ask.py"
  install -m 644 "$HERE/nova-ask.service" /etc/systemd/system/nova-ask.service
  if [ ! -f "$ENVF" ]; then
    ( umask 077; cat > "$ENVF" <<'EOF'
# Nova 질문 서버 설정 (root만 읽을 수 있어요: 권한 600)
# 키는 'sudo bash install.sh set-key'로 넣어요. 이 파일을 화면에 띄우거나 남에게 보내지 마세요.
ANTHROPIC_API_KEY=
NOVA_MODEL=claude-sonnet-5-5
NOVA_MAX_TOKENS=700
NOVA_PER_IP_HOUR=20
NOVA_DAILY_MAX=300
NOVA_FAKE=0
EOF
    )
  fi
  chown root:root "$ENVF"; chmod 600 "$ENVF"
  systemctl daemon-reload
  systemctl enable --now nova-ask
  systemctl restart nova-ask
  sleep 1
  curl -s --max-time 5 http://127.0.0.1:8787/ask/health >/dev/null && echo "서버 프로그램이 127.0.0.1:8787에서 켜졌어요." || die "서버가 켜지지 않았어요: sudo journalctl -u nova-ask -n 30"

  if [ "$mode" = "none" ]; then
    say "https 설정은 건너뛰었어요(NOVA_NO_HTTPS=1). README의 nginx/apache 설정을 넣어 주세요."; return
  fi

  say "3) Caddy(https 자동 인증서) 준비"
  if ! command -v caddy >/dev/null; then
    apt-get update
    apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
    chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
    apt-get update
    apt-get install -y caddy
    # 새로 깐 Caddy의 기본 설정(:80 환영 쪽)은 우리 설정으로 바꿔요
    [ -f /etc/caddy/Caddyfile ] && cp /etc/caddy/Caddyfile "/etc/caddy/Caddyfile.bak.$(date +%Y%m%d%H%M%S)"
    : > /etc/caddy/Caddyfile
  fi
  if grep -q "$DOMAIN" /etc/caddy/Caddyfile 2>/dev/null; then
    echo "Caddyfile에 이미 $DOMAIN 이 있어요. 그대로 둘게요."
  else
    cp /etc/caddy/Caddyfile "/etc/caddy/Caddyfile.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
    cat >> /etc/caddy/Caddyfile <<EOF

# Nova 질문 서버 (install.sh가 넣음): https://$DOMAIN/ask → 127.0.0.1:8787
$DOMAIN {
	handle /ask* {
		reverse_proxy 127.0.0.1:8787
	}
	handle {
		respond "Nova ask server" 404
	}
}
EOF
  fi
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null || die "Caddyfile에 문제가 있어요: sudo caddy validate --config /etc/caddy/Caddyfile"
  systemctl enable --now caddy
  systemctl reload caddy || systemctl restart caddy

  if command -v ufw >/dev/null && ufw status 2>/dev/null | grep -q "Status: active"; then
    say "서버 안 방화벽(ufw)이 켜져 있어 80·443을 열어요"
    ufw allow 80/tcp; ufw allow 443/tcp
  fi

  say "다 됐어요"
  cat <<EOF
- 다음 순서: (1) Lightsail 방화벽에서 80·443 열기(README 2단계)
            (2) sudo bash install.sh set-key  (API 키 넣기)
            (3) sudo bash install.sh check    (동작 확인)
- config.js에 넣을 주소: askUrl: "https://$DOMAIN/ask"
- 인증서는 Caddy가 자동으로 받아요. Lightsail 방화벽에서 80·443을 연 뒤 1~2분 기다리면 https가 열려요.
EOF
}

case "${1:-install}" in
  install) cmd_install ;;
  set-key) cmd_set_key ;;
  check)   cmd_check ;;
  fake)    cmd_fake "${2:-}" ;;
  *) die "알 수 없는 명령: $1 (install | set-key | check | fake on|off)" ;;
esac
