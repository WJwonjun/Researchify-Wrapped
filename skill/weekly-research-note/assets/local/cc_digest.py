#!/usr/bin/env python3
"""Claude Code SessionEnd 훅: 세션을 짧게 요약해 로그 폴더에 저장한다.

python3 표준 라이브러리만 쓴다. install-newsletter-hook.sh 가 설치하고,
저장 위치는 ~/.claude/hooks/cc-digest.dir 에 적혀 있다.
결과: <로그 폴더>/<ISO 주차>/<호스트>-<세션 앞 8자>.md
"""
import datetime, json, os, re, shutil, socket, sys

CONF = os.path.expanduser("~/.claude/hooks/cc-digest.dir")
KEEP_WEEKS = 6
SECRETS = [
    (re.compile(r"(sk-|ghp_|AKIA)[A-Za-z0-9_\-]{12,}"), "[REDACTED]"),
    (re.compile(r"((?i:api[_-]?key|token|secret|password)\s*[:=]\s*)\S+"), r"\1[REDACTED]"),
]


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def redact(s):
    for pat, rep in SECRETS:
        s = pat.sub(rep, s)
    return s


def digest(transcript, session, project, out_dir):
    prompts, files, errors = [], [], []
    with open(transcript, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            content = (e.get("message") or {}).get("content")
            if e.get("type") == "user":
                if not e.get("isMeta"):
                    t = text_of(content).strip()
                    if t and not t.startswith("<"):
                        prompts.append(t)
                for b in content if isinstance(content, list) else []:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                        c = b.get("content")
                        if not isinstance(c, str):
                            c = " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
                        errors.append(" ".join(c.split())[:300])
            elif e.get("type") == "assistant" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and re.search("Edit|Write", b.get("name", "")):
                        p = (b.get("input") or {}).get("file_path")
                        if p and p not in files:
                            files.append(p)
    if not prompts:
        return

    now = datetime.datetime.now().astimezone()   # 서버 시간대를 포함해 기록한다 (수집 마감 계산용)
    year, week, _ = now.isocalendar()
    week_dir = os.path.join(out_dir, f"{year}-W{week:02d}")
    os.makedirs(week_dir, exist_ok=True)
    host = socket.gethostname().split(".")[0]
    lines = [f"# {os.path.basename(project.rstrip('/')) or project} · {now:%Y-%m-%d %a %H:%M %z} · {session}", "", "## 내 입력"]
    for t in prompts:
        lines += ["> " + l for l in t.splitlines()]
    lines += ["", "## 수정한 파일"] + ["- " + p for p in files]
    lines += ["", "## 에러"] + ["- " + e for e in errors]
    with open(os.path.join(week_dir, f"{host}-{session[:8]}.md"), "w", encoding="utf-8") as f:
        f.write(redact("\n".join(lines)) + "\n")

    # 오래된 주차 폴더 정리 (이 훅이 만든 폴더만)
    cy, cw, _ = (now - datetime.timedelta(weeks=KEEP_WEEKS)).isocalendar()
    for d in os.listdir(out_dir):
        m = re.fullmatch(r"(\d{4})-W(\d{2})", d)
        if m and (int(m.group(1)), int(m.group(2))) < (cy, cw):
            shutil.rmtree(os.path.join(out_dir, d), ignore_errors=True)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    transcript = data.get("transcript_path") or ""
    out_dir = os.environ.get("CC_DIGEST_DIR")
    if not out_dir and os.path.exists(CONF):
        out_dir = open(CONF, encoding="utf-8").read().strip()
    if not out_dir or not os.path.isfile(transcript):
        return
    args = (transcript, data.get("session_id") or "unknown", data.get("cwd") or "", out_dir)

    if os.environ.get("CC_DIGEST_FOREGROUND") == "1":
        digest(*args)
        return
    # 세션 종료 시 훅이 일찍 끊길 수 있어, 분리된 백그라운드 프로세스에서 처리하고 바로 반환한다.
    if os.fork() > 0:
        return
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    try:
        digest(*args)
    except Exception:
        pass
    os._exit(0)


if __name__ == "__main__":
    main()
