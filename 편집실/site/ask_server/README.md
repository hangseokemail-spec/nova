# Nova '무엇이든 물어보세요' 답하는 서버 설치 안내

정식 사이트(깃허브 페이지)에서 서아가 질문하면 바로 답이 나오게 하는 작은 서버예요.
AWS Lightsail 우분투 서버(서울, 고정 IP `3.34.169.45`)에 한 번만 설치하면 돼요.

- 서버 프로그램: `nova_ask.py` (파이썬 기본 기능만 씀, 서버 안쪽 `127.0.0.1:8787`에서만 기다림)
- 바깥 주소(https): `https://3-34-169-45.sslip.io/ask` (Caddy가 인증서를 자동으로 받아 `/ask`만 안쪽으로 넘겨 줌)
- API 키: 서버의 `/etc/nova-ask.env` 파일에만 있어요(권한 600, root만 읽기). 저장소·화면·사이트에는 남지 않아요.
- 남용 막기: 질문 300자까지, 답 길이 상한 700토큰, 한 IP당 한 시간 20번, 하루 전체 300번(바꿀 수 있음), Nova 사이트와 claude.ai 미리보기에서 온 요청만 받음.
- 답하는 규칙(4학년 눈높이)은 서버에 고정돼 있어요. 브라우저가 보낸 다른 지시는 쓰지 않아요.
- 메모리: 서버 프로그램 약 20MB, Caddy 약 30~50MB. 1GB 서버에서 다른 일과 함께 돌려도 괜찮아요.

---

## 1단계. Lightsail에 접속하기

Lightsail 콘솔 → 인스턴스 → **'브라우저를 사용하여 연결'(Connect using SSH)** 을 눌러 검은 창을 엽니다.
아래 명령을 **한 덩어리씩** 복사해 붙여 넣고 Enter를 누르세요.

먼저 보안 업데이트를 권해요(몇 분 걸릴 수 있어요. 커널이 바뀌었다고 나오면 Lightsail 콘솔에서 '재부팅').

```bash
sudo apt update && sudo apt upgrade -y
```

## 2단계. Lightsail 방화벽에서 80·443 열기 (콘솔에서 한 번)

https 인증서를 받고 사이트가 질문을 보내려면 두 문이 열려 있어야 해요.

1. Lightsail 콘솔 → 해당 인스턴스 → **네트워킹(Networking)** 탭
2. **IPv4 방화벽** → **규칙 추가(+ Add rule)**
   - 애플리케이션: **HTTP** (TCP 80) → 저장
   - 다시 규칙 추가 → 애플리케이션: **HTTPS** (TCP 443) → 저장
3. IPv6 방화벽이 켜져 있으면 같은 두 규칙을 거기에도 추가해요.

(이미 다른 웹사이트를 운영 중이라 열려 있으면 그대로 두면 돼요.)

## 3단계. 파일 받기

```bash
mkdir -p ~/nova-ask && cd ~/nova-ask
B="https://raw.githubusercontent.com/hangseokemail-spec/nova/main/%ED%8E%B8%EC%A7%91%EC%8B%A4/site/ask_server"
for f in nova_ask.py nova-ask.service install.sh; do curl -fsSLO "$B/$f" || echo "받기 실패: $f"; done
ls -l
```

`nova_ask.py`, `nova-ask.service`, `install.sh` 세 파일이 보이면 됩니다.

## 4단계. 설치

```bash
cd ~/nova-ask && sudo bash install.sh
```

설치 스크립트가 하는 일:
- 서버 프로그램을 `/opt/nova-ask/`에 넣고, 시스템 서비스 `nova-ask`로 켜요(서버를 다시 켜도 자동으로 켜짐).
- `/etc/nova-ask.env`(설정 파일, 권한 600)를 만들어요. 키 칸은 비어 있어요.
- 80·443 포트가 **비어 있으면** Caddy를 설치해 `3-34-169-45.sslip.io` 인증서를 자동으로 받고 `/ask`를 서버 프로그램으로 넘겨요.
- 80·443을 **이미 nginx나 apache가 쓰고 있으면** Caddy를 깔지 않고 멈춰요. 그때는 아래 '이미 nginx나 apache를 쓰고 있다면'을 보세요.
- 서버 안 방화벽(ufw)이 켜져 있으면 80·443을 열어요.

## 5단계. API 키 넣기 (편집인이 직접)

```bash
cd ~/nova-ask && sudo bash install.sh set-key
```

"Anthropic API 키를 붙여 넣고…"가 나오면 키를 붙여 넣고 Enter를 누르세요.
**입력한 키는 화면에 보이지 않는 게 정상**이에요. 키는 `/etc/nova-ask.env`에만 저장되고, 명령 기록(history)에도 남지 않아요.
(브라우저 SSH 창에서 붙여 넣기가 안 되면 창 오른쪽 아래의 클립보드 아이콘에 키를 넣은 뒤, 창 안에서 마우스 오른쪽 단추나 Ctrl+Shift+V로 붙여 넣어요.)

키를 바꾸고 싶을 때도 같은 명령을 다시 쓰면 돼요. 키는 채팅, 이메일, 저장소 어디에도 적지 마세요.

## 6단계. 동작 확인

```bash
cd ~/nova-ask && sudo bash install.sh check
```

다음처럼 나오면 성공이에요.
- `nova-ask 켜져 있음`
- `{"ok": true, "fake": false, "key": true, ...}`
- 마지막 줄에 `{"a": "하늘이 파란 까닭은 ..."}` 처럼 답이 나옴

직접 확인하고 싶으면:

```bash
curl -s https://3-34-169-45.sslip.io/ask/health; echo
curl -s -X POST https://3-34-169-45.sslip.io/ask -H 'Origin: https://hangseokemail-spec.github.io' -H 'Content-Type: text/plain' --data '{"q":"별은 왜 반짝여요?","issue":2}'; echo
```

https가 안 열리면(방화벽을 막 연 경우) 1~2분 기다렸다가 다시 해 보세요. 그래도 안 되면 `sudo journalctl -u caddy -n 50`을 보세요.

## 7단계. 사이트에 주소 넣기 (진행 담당 또는 편집인)

저장소 맨 위 `config.js`의 `askUrl`에 주소를 넣고 커밋·push 하면 정식 사이트에서 바로 답이 나와요.

```js
window.SEOA_CONFIG = { gasUrl: "", askUrl: "https://3-34-169-45.sslip.io/ask" };
```

---

## 설정 바꾸기

`sudo nano /etc/nova-ask.env` 로 열어 숫자를 바꾼 뒤 `sudo systemctl restart nova-ask`.
(이 파일에는 키가 있으니 화면을 다른 사람에게 보여 주지 마세요.)

| 이름 | 기본값 | 뜻 |
|---|---|---|
| `NOVA_MODEL` | `claude-sonnet-5-5` | 답하는 모델 |
| `NOVA_MAX_TOKENS` | `700` | 답 길이 상한 |
| `NOVA_PER_IP_HOUR` | `20` | 한 IP가 한 시간에 물을 수 있는 횟수 |
| `NOVA_DAILY_MAX` | `300` | 하루(한국 시각) 전체 질문 상한. 요금이 걱정되면 줄여요 |
| `NOVA_FAKE` | `0` | `1`이면 API를 부르지 않고 '시험용 답'만 돌려줘요 |
| `NOVA_ALLOWED_ORIGINS` | (비어 있음) | 더 허용할 사이트 주소(쉼표로 구분) |

- 키 없이 연결만 시험하기: `sudo bash install.sh fake on` → 확인 뒤 `sudo bash install.sh fake off`
- 기록 보기: `sudo journalctl -u nova-ask -n 50` (질문 내용은 기록하지 않고 글자 수와 걸린 시간만 남겨요)
- 잠시 끄기: `sudo systemctl stop nova-ask` / 다시 켜기: `sudo systemctl start nova-ask`
- 횟수 기록은 서버 프로그램을 다시 켜면 처음부터 다시 세요.
- Anthropic 콘솔에서 이 키에 **월 사용 한도**를 걸어 두면 더 안전해요.

## 이미 nginx나 apache를 쓰고 있다면

설치 스크립트가 멈췄다면, 서버 프로그램만 먼저 깔아요.

```bash
cd ~/nova-ask && sudo NOVA_NO_HTTPS=1 bash install.sh
```

그다음 이미 https가 붙은 사이트(예: `example.com`) 설정에 아래 줄을 넣어요. 그러면 주소는 `https://example.com/ask`가 되고, `config.js`의 `askUrl`에 그 주소를 넣어요.
(https 인증서가 없는 사이트라면 Caddy 쪽이 더 쉬워요. 이때는 Caddy를 다른 포트로 돌리기보다, 기존 웹서버에 인증서를 붙이는 편이 좋아요. 예: `sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx`)

**nginx** (`/etc/nginx/sites-available/<사이트 파일>`의 `server { listen 443 ssl; ... }` 안):

```nginx
location /ask {
    proxy_pass http://127.0.0.1:8787;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 60s;
    client_max_body_size 16k;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**apache** (`<VirtualHost *:443>` 안. 먼저 `sudo a2enmod proxy proxy_http`):

```apache
ProxyPass        /ask http://127.0.0.1:8787/ask
ProxyPassReverse /ask http://127.0.0.1:8787/ask
ProxyTimeout 60
```

```bash
sudo apachectl configtest && sudo systemctl reload apache2
```

## 지우기

```bash
sudo systemctl disable --now nova-ask
sudo rm -f /etc/systemd/system/nova-ask.service /etc/nova-ask.env
sudo rm -rf /opt/nova-ask
sudo systemctl daemon-reload
```
Caddy까지 지우려면 `/etc/caddy/Caddyfile`에서 `# Nova 질문 서버` 아래 덩어리를 지우거나 `sudo apt remove caddy`.

## 파일

- `nova_ask.py` 서버 프로그램 / `nova-ask.service` 시스템 서비스 / `install.sh` 설치·키 넣기·확인
- `test_nova_ask.py` 키 없이 하는 시험(CORS, 글자 수, 횟수 제한): `python3 test_nova_ask.py`
