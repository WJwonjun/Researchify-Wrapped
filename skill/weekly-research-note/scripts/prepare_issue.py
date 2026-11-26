"""issue.json 과 그림 SVG를 허브 페이지 데이터베이스에 쓸 문서들로 바꾼다.

    python prepare_issue.py issue.json OUT_DIR

결과: OUT_DIR/writes.json (Artifact write_db batch의 writes 목록) 과 문서별 JSON 파일.
문제가 있으면 무엇을 고쳐야 하는지 출력하고 1로 끝난다.
"""
import datetime, json, os, re, sys

SEG = re.compile(r"^[A-Za-z0-9_\-.~:@+]{1,200}$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BLOCK_FIELDS = {
    "p": ["text"], "h2": ["text"], "bullets": ["items"], "quote": ["text"],
    "paper": ["title"], "figure": ["path", "caption"], "equation": ["path"],
    "code": ["lines"], "callout": ["title"],
}
MAX_DOC = 250 * 1024
ITEM_ID = re.compile(r"^[A-Za-z0-9_.\-]{1,40}$")
ITEM_KINDS = {"paper", "news", "figure", "concept", "tip", "other"}
NEEDS_ITEM = {"paper", "figure"}   # 반응 버튼이 꼭 달려야 하는 블록
errors = []


def err(msg):
    errors.append(msg)


def check_links(text, where):
    for _, url in LINK.findall(text or ""):
        if not url.startswith(("https://", "http://")):
            err(f"{where}: 링크는 http(s) 주소만 쓸 수 있어요 ({url})")


def load_svg(path, where):
    if not os.path.isfile(path):
        err(f"{where}: 그림 파일이 없어요 ({path})")
        return None
    svg = open(path, encoding="utf-8").read()
    low = svg.lower()
    if "<svg" not in low:
        err(f"{where}: SVG 파일이 아니에요 ({path})")
    if "<script" in low or re.search(r"\son\w+\s*=", low) or "javascript:" in low:
        err(f"{where}: SVG 안에 스크립트가 있어요. figstyle로 다시 그리세요 ({path})")
    return svg


def main(src, out):
    base = os.path.dirname(os.path.abspath(src))
    issue = json.load(open(src, encoding="utf-8"))
    week = str(issue.get("week", ""))
    if not SEG.match(week):
        err("week: 2026-W48 같은 형식이어야 해요 (영문·숫자·하이픈)")
    for f in ["title", "summary", "sections"]:
        if not issue.get(f):
            err(f"{f}: 비어 있어요")
    if len(issue.get("cards", [])) not in (0, 4):
        err("cards: 0장 또는 4장이어야 해요")

    items = issue.get("items") or {}
    if not isinstance(items, dict):
        err("items: {항목 id: {kind, title, ...}} 형태여야 해요")
        items = {}
    for iid, meta in items.items():
        if not ITEM_ID.match(iid):
            err(f"items.{iid}: id는 영문·숫자·점·하이픈·밑줄 40자 이내로")
        if not isinstance(meta, dict) or meta.get("kind") not in ITEM_KINDS or not meta.get("title"):
            err(f"items.{iid}: kind({'/'.join(sorted(ITEM_KINDS))})와 title이 필요해요")
    qs = issue.get("questions") or []
    if len(qs) > 2:
        err("questions: 호당 2개 이내로")
    for q in qs:
        if not re.match(r"^Q\d+$", str(q.get("id", ""))) or not q.get("text"):
            err("questions: 각 질문에 id(Q1, Q2…)와 text가 필요해요")
        if q.get("options") is not None and (not isinstance(q["options"], list) or len(q["options"]) < 2):
            err(f"questions.{q.get('id')}: options는 2개 이상인 목록이어야 해요")

    os.makedirs(out, exist_ok=True)
    writes, figs = [], []

    def convert(blocks, where):
        for i, b in enumerate(blocks):
            w = f"{where} 블록 {i + 1}"
            t = b.get("type")
            if t not in BLOCK_FIELDS:
                err(f"{w}: 모르는 type '{t}'")
                continue
            for f in BLOCK_FIELDS[t]:
                if not b.get(f):
                    err(f"{w} ({t}): {f} 가 비어 있어요")
            for k in ("text", "caption", "title"):
                check_links(b.get(k), w)
            if b.get("item") is not None and b["item"] not in items:
                err(f"{w}: item '{b['item']}' 이(가) issue.items 에 없어요")
            if t in NEEDS_ITEM and not b.get("item"):
                err(f"{w} ({t}): 반응을 받을 수 있게 item id를 붙이고 issue.items 에 등록하세요")
            for it in b.get("items", []):
                check_links(it, w)
            if t in ("figure", "equation") and b.get("path"):
                svg = load_svg(os.path.join(base, b["path"]), w)
                if svg is None:
                    continue
                kind = "f" if t == "figure" else "e"
                fid = f"{week}-{kind}{sum(1 for x in figs if x.startswith(f'{week}-{kind}')) + 1}"
                doc = {"week": week, "kind": t, "svg": svg}
                size = len(json.dumps(doc, ensure_ascii=False).encode())
                if size > MAX_DOC:
                    err(f"{w}: 그림이 너무 커요 ({size // 1024} KB > 250 KB). 점·선 수를 줄이세요")
                p = os.path.join(out, f"figure-{fid}.json")
                json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False)
                figs.append(fid)
                writes.append({"op": "set", "collection": "figures", "doc_id": fid, "file_path": os.path.abspath(p)})
                del b["path"]
                b["fig"] = fid

    for s in issue.get("sections", []):
        for f in ["num", "label", "heading", "blocks"]:
            if not s.get(f):
                err(f"섹션 {s.get('num', '?')}: {f} 가 비어 있어요")
        convert(s.get("blocks", []), f"섹션 {s.get('num', '?')}")
    convert(issue.get("monthly_review", []), "월간 점검")
    for r in issue.get("references", []):
        if r.get("url"):
            check_links(f"[x]({r['url']})", "참고문헌")
    if sum(1 for f in figs if "-f" in f) > 3:
        err("그림은 호 전체에서 3장 이내로 해 주세요")

    issue["published"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    size = len(json.dumps(issue, ensure_ascii=False).encode())
    if size > MAX_DOC:
        err(f"issue 문서가 너무 커요 ({size // 1024} KB > 250 KB)")
    if errors:
        print("고칠 것:")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    p = os.path.join(out, f"issue-{week}.json")
    json.dump(issue, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    writes.insert(0, {"op": "set", "collection": "issues", "doc_id": week, "file_path": os.path.abspath(p)})
    json.dump(writes, open(os.path.join(out, "writes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"준비 완료: 문서 {len(writes)}개 (호 1, 그림·수식 {len(figs)})")
    print(f"다음: Artifact write_db, db_op=batch, writes = {os.path.join(out, 'writes.json')} 의 내용")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
