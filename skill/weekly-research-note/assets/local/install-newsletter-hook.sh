#!/usr/bin/env bash
# 주간 리서치 노트: Claude Code 훅 설치 (Mac, Linux 서버 공통, python3만 필요)
# 사용법: cc_digest.py 와 같은 폴더에서  bash install-newsletter-hook.sh [로그 폴더]
#   폴더를 주지 않으면 ~/claude-newsletter 를 쓴다. 로그는 이 컴퓨터 밖으로 나가지 않는다.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_DIR="$HOME/.claude/hooks"
SETTINGS="$HOME/.claude/settings.json"
say() { printf '%s\n' "$*"; }
die() { printf '중단: %s\n' "$*" >&2; exit 1; }

# 1. 준비물 확인
command -v python3 >/dev/null 2>&1 || die "python3 가 필요해요."
[ -f "$SRC_DIR/cc_digest.py" ] || die "cc_digest.py 를 이 스크립트와 같은 폴더에 두세요."

# 2. 로그 폴더
BASE="${1:-$HOME/claude-newsletter}"
mkdir -p "$BASE/cc-log"

# 3. 훅 복사
mkdir -p "$HOOK_DIR"
cp "$SRC_DIR/cc_digest.py" "$HOOK_DIR/cc_digest.py"
chmod +x "$HOOK_DIR/cc_digest.py"
printf '%s' "$BASE/cc-log" > "$HOOK_DIR/cc-digest.dir"

# 4. settings.json 에 등록 (기존 설정 유지, 예전 bash 버전 훅은 교체)
python3 - "$SETTINGS" "python3 \"$HOOK_DIR/cc_digest.py\"" << 'PY'
import json, os, shutil, sys, time
path, cmd = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except ValueError:
        sys.exit(f"중단: {path} 가 올바른 JSON이 아니에요. 확인 후 다시 실행하세요.")
groups = data.setdefault("hooks", {}).setdefault("SessionEnd", [])
before = json.dumps(groups, sort_keys=True)
for g in groups:
    g["hooks"] = [h for h in g.get("hooks", []) if "cc-digest.sh" not in h.get("command", "")]
groups[:] = [g for g in groups if g.get("hooks")]
if not any(h.get("command") == cmd for g in groups for h in g.get("hooks", [])):
    groups.append({"hooks": [{"type": "command", "command": cmd}]})
if json.dumps(groups, sort_keys=True) != before:
    if os.path.exists(path):
        shutil.copy(path, f"{path}.bak.{time.strftime('%Y%m%d%H%M%S')}")
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("settings.json 에 훅을 등록했어요.")
else:
    print("훅이 이미 등록되어 있어요.")
if data.get("cleanupPeriodDays") == 0:
    print("주의: cleanupPeriodDays 가 0이에요. 세션 기록이 저장되지 않을 수 있으니 30 이상으로 바꾸세요.")
PY

# 5. 가짜 세션으로 자체 테스트 (실제 로그 폴더에는 쓰지 않음)
T=$(mktemp -d)
printf '%s\n' '{"type":"user","message":{"role":"user","content":"설치 테스트"}}' > "$T/t.jsonl"
printf '{"transcript_path":"%s","session_id":"selftest0000","cwd":"/tmp/demo"}' "$T/t.jsonl" \
  | CC_DIGEST_FOREGROUND=1 CC_DIGEST_DIR="$T/out" python3 "$HOOK_DIR/cc_digest.py"
ls "$T"/out/*/*.md >/dev/null 2>&1 || die "자체 테스트 실패: 훅이 파일을 만들지 못했어요."
rm -rf "$T"
say "설치 완료 ($(hostname -s)): 로그 폴더 $BASE/cc-log"
