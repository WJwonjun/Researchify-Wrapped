"""주간 리서치 노트를 새 사용자에게 설정하는 도구.

    python setup_kit.py capabilities            # 허브 페이지를 발행할 때 넣을 capabilities(JSON)를 출력
    python setup_kit.py render config.json OUT  # 프롬프트·초기 데이터·샘플 호·시작 문구를 OUT에 만든다

render가 만드는 것:
  OUT/writes.json      Artifact write_db batch에 그대로 넣을 목록 (프롬프트, 가이드, 그림 코드, 선호 기록, 샘플 호)
  OUT/bootstraps.md    스케줄 작업에 한 번 붙여 넣을 시작 문구
  OUT/local/           Claude Code 로그용 설치 파일 (Claude Code 수집을 켠 경우)
  OUT/project-collect/ 프로젝트별 수동 수집 지침 (채팅 수집을 켠 경우, 예비용)
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
T = os.path.join(SKILL, "assets", "templates")

OWNER_ONLY = ["feedback", "feedback_tags", "ledger", "experiments", "chatlog", "cclog",
              "prefs", "skill", "skill_history", "prompts"]
CAPABILITIES = {
    "comments": {"composer_only": True},
    "user": {},
    "db": {"rules": [{"path": "", "read": "view", "write": "owner"}]
           + [{"path": p, "read": "owner", "write": "owner"} for p in OWNER_ONLY]},
}
DEFAULTS = {
    "tz_name": "한국 시간(UTC+9)",
    "interests": "",
    "tier1_ml": ["NeurIPS", "ICML", "ICLR"],
    "tier1_sys": ["OSDI", "NSDI", "SOSP", "ASPLOS", "MLSys", "MobiSys"],
    "exception_orgs": ["MIT", "Stanford", "UC Berkeley", "CMU", "UW", "Google DeepMind", "Meta",
                       "Microsoft Research", "NVIDIA"],
    "projects": [],
    "sources": {"claude_code": True, "chat": True},
    "schedule": {"cc": "매주 금요일 22:00", "chat": "매주 금요일 22:30", "publish": "매주 토요일 09:00"},
}
SLUG = re.compile(r"^[A-Za-z0-9_.\-]{1,60}$")


def die(msg):
    print("고칠 것:", msg)
    sys.exit(1)


def fill(text, values):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        die(f"채워지지 않은 값: {sorted(set(left))}")
    return text


def keep_block(text, tag, keep):
    pat = re.compile(rf"<!--{tag}-->\n?(.*?)<!--/{tag}-->\n?", re.S)
    return pat.sub(lambda m: m.group(1) if keep else "", text)


def render(cfg_path, out):
    cfg = {**DEFAULTS, **json.load(open(cfg_path, encoding="utf-8"))}
    cfg["sources"] = {**DEFAULTS["sources"], **cfg.get("sources", {})}
    cfg["schedule"] = {**DEFAULTS["schedule"], **cfg.get("schedule", {})}
    hub = cfg.get("hub_url", "")
    if not re.match(r"^https://claude\.ai/artifact/[A-Za-z0-9]+$", hub):
        die("hub_url: 허브 페이지를 먼저 발행하고 그 주소를 넣으세요 (https://claude.ai/artifact/...)")
    projects = cfg["projects"]
    for p in projects:
        if not p.get("name") or not SLUG.match(p.get("slug", "")):
            die(f"projects: name과 slug(영문·숫자·밑줄·하이픈)가 필요해요 → {p}")
    if len({p["slug"] for p in projects}) != len(projects):
        die("projects: slug가 겹쳐요")
    use_cc = bool(cfg["sources"]["claude_code"])
    use_chat = bool(cfg["sources"]["chat"]) and bool(projects)

    interests = cfg["interests"].strip()
    values = {
        "HUB_URL": hub,
        "TZ_NAME": cfg["tz_name"],
        "INTERESTS_LINE": (f"나의 연구 관심사: {interests}. 이번 주 로그가 적으면 이 관심사를 기준으로 고른다." if interests
                           else "이번 주 로그가 적으면 지난 호들과 선호 프로필을 기준으로 고른다."),
        "TIER1_VENUES": f"ML: {', '.join(cfg['tier1_ml'])} / Systems: {', '.join(cfg['tier1_sys'])}",
        "EXCEPTION_ORGS": ", ".join(cfg["exception_orgs"]),
        "PROJECT_LIST": "\n".join(f"- 프로젝트 이름: {p['name']} / slug: {p['slug']}" for p in projects),
        "SCHED_PUBLISH": cfg["schedule"]["publish"],
        "SCHED_CC": cfg["schedule"]["cc"],
        "SCHED_CHAT": cfg["schedule"]["chat"],
    }
    os.makedirs(out, exist_ok=True)
    writes = []

    def put(coll, doc_id, data):
        path = os.path.abspath(os.path.join(out, "seed", f"{coll}__{doc_id}.json"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        size = os.path.getsize(path)
        if size > 250 * 1024:
            die(f"{coll}/{doc_id}가 너무 커요 ({size // 1024} KB)")
        writes.append({"op": "set", "collection": coll, "doc_id": doc_id, "file_path": path})

    def tpl(name):
        return open(os.path.join(T, name), encoding="utf-8").read()

    today = __import__("datetime").date.today().isoformat()
    put("prompts", "main", {"version": 1, "updated": today, "text": fill(tpl("main.md"), values)})
    if use_cc:
        put("prompts", "cc-collector", {"version": 1, "updated": today, "text": fill(tpl("cc-collector.md"), values)})
    if use_chat:
        put("prompts", "chat-collector", {"version": 1, "updated": today, "text": fill(tpl("chat-collector.md"), values)})
    put("skill", "guide", {"version": 1, "updated": today, "basis": "초기본",
                           "text": open(os.path.join(SKILL, "references", "guide.md"), encoding="utf-8").read()})
    put("skill", "figstyle", {"version": 1, "updated": today, "basis": "초기본",
                              "code": open(os.path.join(HERE, "figstyle.py"), encoding="utf-8").read()})
    put("prefs", "main", {"note": "profile: ledger에서 계산한 선호. rules: 프롬프트보다 우선하는 규칙. ops_notes: 운영 메모.",
                          "profile": {}, "rules": [], "ops_notes": []})

    # 디자인을 바로 볼 수 있게 샘플 호를 함께 올린다 (첫 정식 호가 나오면 메인 작업이 지운다)
    sdir = os.path.join(out, "sample")
    os.makedirs(sdir, exist_ok=True)
    shutil.copy(os.path.join(SKILL, "references", "example-issue.json"), os.path.join(sdir, "issue.json"))
    for f in os.listdir(os.path.join(SKILL, "assets", "sample")):
        shutil.copy(os.path.join(SKILL, "assets", "sample", f), sdir)
    r = subprocess.run([sys.executable, os.path.join(HERE, "prepare_issue.py"), os.path.join(sdir, "issue.json"),
                        os.path.join(sdir, "out")], capture_output=True, text=True)
    if r.returncode != 0:
        die("샘플 호 준비 실패\n" + r.stdout + r.stderr)
    writes += json.load(open(os.path.join(sdir, "out", "writes.json"), encoding="utf-8"))

    b = keep_block(keep_block(tpl("bootstraps.md"), "CC", use_cc), "CHAT", use_chat)
    open(os.path.join(out, "bootstraps.md"), "w", encoding="utf-8").write(fill(b, values))
    if use_cc:
        shutil.copytree(os.path.join(SKILL, "assets", "local"), os.path.join(out, "local"), dirs_exist_ok=True)
    if use_chat:
        pdir = os.path.join(out, "project-collect")
        os.makedirs(pdir, exist_ok=True)
        for p in projects:
            text = fill(tpl("project-collect.md"), {**values, "PROJECT_NAME": p["name"], "PROJECT_SLUG": p["slug"]})
            open(os.path.join(pdir, f"{p['slug']}.md"), "w", encoding="utf-8").write(text)
    json.dump(writes, open(os.path.join(out, "writes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"준비 완료: 허브에 쓸 문서 {len(writes)}개")
    print(f"  Claude Code 수집: {'켜짐' if use_cc else '꺼짐'} / 채팅 수집: {'켜짐 (' + str(len(projects)) + '개 프로젝트)' if use_chat else '꺼짐'}")
    print(f"다음: Artifact write_db, db_op=batch, writes = {os.path.join(out, 'writes.json')} 의 내용")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "capabilities":
        print(json.dumps(CAPABILITIES, ensure_ascii=False))
    elif len(sys.argv) == 4 and sys.argv[1] == "render":
        render(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
