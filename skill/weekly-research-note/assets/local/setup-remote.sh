#!/usr/bin/env bash
# 주간 리서치 노트: 원격 서버들에 훅을 설치하고, 이 Mac이 하루 네 번(0·6·12·18시 1분)과 금요일 21:55에 서버 로그를 가져오게 설정한다.
# 사용법: install-newsletter-hook.sh, cc_digest.py 와 같은 폴더에서
#   bash setup-remote.sh 서버1 서버2 ...
# 서버 이름은 ~/.ssh/config 의 Host 별칭이나 user@host. 서버를 추가할 때도 새 서버만 넣어 다시 실행한다.
set -uo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/claude-newsletter"
LIST="$BASE/servers.txt"
AGENT_ID="com.claude-newsletter.pull"
PLIST="$HOME/Library/LaunchAgents/$AGENT_ID.plist"
say() { printf '%s\n' "$*"; }
die() { printf '중단: %s\n' "$*" >&2; exit 1; }

[ "$(uname)" = "Darwin" ] || die "이 스크립트는 Mac에서 실행하세요."
[ $# -ge 1 ] || die "서버 이름을 하나 이상 넣어 주세요. 예: bash setup-remote.sh gpu1 gpu2"
for f in install-newsletter-hook.sh cc_digest.py; do
  [ -f "$SRC_DIR/$f" ] || die "$f 를 이 스크립트와 같은 폴더에 두세요."
done
mkdir -p "$BASE/cc-log"; touch "$LIST"

# 1. 서버마다 훅 설치 (비밀번호나 2단계 인증을 물으면 입력하세요)
RESULTS=()
for h in "$@"; do
  say ""; say "── $h"
  if ssh -o ConnectTimeout=15 "$h" 'mkdir -p ~/.cache/claude-newsletter-setup' \
     && scp -q -o ConnectTimeout=15 "$SRC_DIR/install-newsletter-hook.sh" "$SRC_DIR/cc_digest.py" "$h":.cache/claude-newsletter-setup/ \
     && ssh -o ConnectTimeout=15 "$h" 'bash ~/.cache/claude-newsletter-setup/install-newsletter-hook.sh'; then
    inst="설치됨"
  else
    inst="설치 실패"
  fi
  if ssh -n -o BatchMode=yes -o ConnectTimeout=15 "$h" true 2>/dev/null; then key="키 인증 됨"; else key="키 인증 안 됨"; fi
  grep -qxF "$h" "$LIST" || echo "$h" >> "$LIST"
  RESULTS+=("$h|$inst|$key")
done

# 2. 가져오기 스크립트 (서버마다 ~/claude-newsletter/cc-log 를 통째로 받아 이 Mac의 같은 폴더에 합친다)
cat > "$BASE/cc-pull.sh" << 'PULL'
#!/bin/bash
# 원격 서버들의 Claude Code 로그를 이 Mac으로 가져온다. launchd가 하루 네 번, 수집 작업이 실행 직전에 한 번 더 실행한다.
set -o pipefail
BASE="$HOME/claude-newsletter"
TMP="$BASE/last-pull.txt.tmp"
echo "# $(date '+%Y-%m-%d %H:%M') 가져오기 결과" > "$TMP"
while IFS= read -r h || [ -n "$h" ]; do
  h="${h%%#*}"; h="${h//[[:space:]]/}"; [ -z "$h" ] && continue
  if ssh -n -o BatchMode=yes -o ConnectTimeout=15 "$h" 'cd ~/claude-newsletter && tar czf - cc-log' 2>>"$BASE/pull.err" \
       | tar xzf - -C "$BASE" 2>>"$BASE/pull.err"; then
    echo "성공 $h" >> "$TMP"
  else
    echo "실패 $h" >> "$TMP"
  fi
done < "$BASE/servers.txt"
mv "$TMP" "$BASE/last-pull.txt"
[ -f "$BASE/pull.err" ] && tail -n 200 "$BASE/pull.err" > "$BASE/pull.err.tmp" && mv "$BASE/pull.err.tmp" "$BASE/pull.err"
exit 0
PULL
chmod +x "$BASE/cc-pull.sh"

# 3. launchd 에 등록 (매일 0·6·12·18시 1분, 금요일 22시 수집 직전인 21:55, 로그인할 때도 한 번. 잠들어 있던 시각의 실행은 깨어날 때 한다)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" << PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$AGENT_ID</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$BASE/cc-pull.sh</string></array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>1</integer></dict>
    <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>1</integer></dict>
    <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>1</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>1</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>55</integer></dict>
  </array>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$BASE/pull.out</string>
  <key>StandardErrorPath</key><string>$BASE/pull.out</string>
</dict>
</plist>
PL
launchctl bootout "gui/$(id -u)/$AGENT_ID" 2>/dev/null || true
rm -f "$BASE/last-pull.txt"
launchctl bootstrap "gui/$(id -u)" "$PLIST" || die "launchd 등록에 실패했어요."

# 4. 등록하자마자 백그라운드에서 한 번 돈다. 그 결과로 실제 자동 수집이 되는지 확인한다.
say ""; say "백그라운드 첫 가져오기를 기다리는 중..."
for _ in $(seq 1 60); do [ -f "$BASE/last-pull.txt" ] && break; sleep 2; done

say ""; say "결과"
for r in "${RESULTS[@]}"; do
  IFS='|' read -r h inst key <<< "$r"
  pull=$(grep -E "^(성공|실패) $h\$" "$BASE/last-pull.txt" 2>/dev/null | cut -d' ' -f1)
  say "  $h: $inst, $key, 자동 가져오기 ${pull:-결과 없음}"
done
say ""
say "자동 가져오기가 실패한 서버가 있으면:"
say "  - '키 인증 안 됨': ssh-copy-id <서버> 로 키를 등록한 뒤 이 스크립트를 다시 실행하세요."
say "  - 키 인증은 되는데 실패: 키 암호를 키체인에 저장하세요 (ssh-add --apple-use-keychain ~/.ssh/<키 파일>)."
say "  - VPN이 필요한 서버는 VPN이 켜져 있을 때만 가져와져요. 하루 네 번 다시 시도해요."
say "상태 확인: cat $BASE/last-pull.txt"
