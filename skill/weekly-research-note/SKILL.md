---
name: weekly-research-note
description: 주간 리서치 노트(개인 뉴스레터)를 만들어 Claude Artifact 허브 페이지에 발행하는 스킬. 주장형 제목, 큰 섹션 번호, 핵심 숫자 카드, 번호 붙은 그림과 캡션, 참고문헌, 별점 피드백으로 이뤄진 정해진 디자인을 허브 페이지 코드에 고정해 두고, 매주 내용만 허브의 데이터베이스에 쓴다. 글쓰기·그림 가이드와 그림 스타일 코드는 허브에 살아 있는 최신본이 있어 작업이 직접 고쳐 쓴다. 처음 쓰는 사람의 설정(허브 발행, 지시문·초기 데이터 생성, 설치 파일과 스케줄 작업 안내)도 이 스킬로 한다. "주간 리서치 노트", "뉴스레터", "이번 주 호"를 만들거나 고치거나 설정할 때는 내용 규칙이 다른 곳에 있더라도 문장, 그림, 발행은 반드시 이 스킬대로 한다.
---

# 주간 리서치 노트 만들기

**처음 설정하는 경우**("설정해 줘", "세팅", "설치")에는 `references/setup.md`를 읽고 그대로 진행한다. 아래는 매주 호를 만드는 방법이다.

내용(어떤 논문·뉴스·주제를 고를지)은 작업 프롬프트가 정한다. 이 스킬은 그 내용을 **어떻게 쓰고, 어떻게 그리고, 어떻게 발행하는지**를 정한다. 허브 주소는 작업 프롬프트에 있다.

이 스킬은 두 부분으로 나뉜다.
- **살아 있는 부분:** 글쓰기·그림 가이드(`skill/guide`)와 그림 스타일 코드(`skill/figstyle`). 허브에 최신본이 있고, 작업이 피드백과 스스로 발견한 개선점에 따라 직접 고쳐 쓴다. 이 스킬 안의 `references/guide.md`와 `scripts/figstyle.py`는 허브를 못 읽을 때 쓰는 기본본이다.
- **고정된 부분:** issue.json 형식, 검사 스크립트(`scripts/prepare_issue.py`), 발행 절차, 허브 페이지 원본(`assets/hub.html`). 정확성과 발행을 지키는 장치라 작업이 고치지 않는다.

## 0. 살아 있는 부분 불러오기 (매 실행 처음)

1. Artifact `read_db`, `db_op: "get"`, `collection: "skill"`, `doc_id: "guide"` → `text`를 이번 실행의 쓰기·그림 규칙으로 쓴다. 없거나 비어 있으면 `references/guide.md`를 쓴다.
2. 같은 방법으로 `doc_id: "figstyle"` → `code`를 작업 폴더의 `figstyle.py`로 저장하고 `python <skill>/scripts/selftest_figstyle.py figstyle.py`를 돌린다. OK면 그 파일을 쓴다. 문서가 없거나 테스트가 실패하면 `<skill>/scripts/figstyle.py`를 작업 폴더로 복사해 쓰고, 실행 결과에 "figstyle 기본본 사용: <이유>"를 남긴다.
3. 두 문서의 `version` 필드와 읽을 때 받은 문서 version을 기억해 둔다 (고칠 때 쓴다).

## 순서

1. 내용을 정한 뒤 0단계에서 불러온 가이드대로 문장을 쓴다.
2. 그림과 수식을 0단계에서 정한 `figstyle.py`로 SVG로 만든다.
3. `issue.json`을 쓴다 (아래 "issue.json 형식"). 그림 경로는 이 파일 기준 상대 경로.
4. 검사와 변환: `python <skill>/scripts/prepare_issue.py issue.json out`
   "고칠 것"이 나오면 고치고 다시 실행한다. 성공하면 `out/writes.json`이 생긴다.
5. 발행: Artifact 도구 `action: "write_db"`, `url: <허브 주소>`, `db_op: "batch"`, `writes: <out/writes.json의 내용 그대로>`.
6. 확인: `action: "read_db"`, `db_op: "get"`, `collection: "issues"`, `doc_id: <week>`로 방금 쓴 호가 있는지 본다.

허브 페이지가 지워졌거나 고장 났을 때만 `assets/hub.html`을 다시 발행한다. 그때는 작업을 멈추고 결과에 그 사실을 적는다 (주소가 바뀌므로 사용자가 프롬프트를 고쳐야 한다).

## 살아 있는 부분 고치기

글쓰기나 그림의 기본 방식을 바꿔야 할 때 쓴다. 규칙을 따로 덧붙이지 말고 가이드나 코드 본문을 직접 고친다.

1. **guide:** 바꿀 부분만 고치고 나머지는 그대로 둔다.
2. **figstyle:** 고친 코드를 작업 폴더에 저장하고 `selftest_figstyle.py`를 통과해야만 허브에 쓴다. `setup`, `figure`, `save`, `equation`과 색 상수의 이름·인자는 바꾸지 않는다. 함수나 상수를 새로 추가하는 것은 된다.
3. **저장:** `write_db`, `db_op: "batch"`로 두 가지를 한 번에 쓴다.
   - `{"op": "set", "collection": "skill_history", "doc_id": "<guide|figstyle>-v<지금 version 필드>", "data": <고치기 전 문서 그대로>}`
   - `{"op": "set", "collection": "skill", "doc_id": "<guide|figstyle>", "data": {"version": <지금 version 필드 + 1>, "updated": "YYYY-MM-DD", "basis": "<무엇 때문에 바꿨는지>", "text": "..." 또는 "code": "..."}, "if_version": <읽을 때 받은 문서 version>}`
4. **알림:** issue.json의 `applied_feedback`에 "가이드 v3: 1-B 설명을 5줄 이내로"처럼 한 줄로 적는다.
5. **되돌리기:** 사용자가 "가이드 되돌려", "그림 스타일 되돌려"라고 하면 `skill_history`의 직전 버전을 `skill/<이름>`에 다시 쓴다 (version 필드는 +1).
6. 고친 내용은 이번 호부터 바로 쓴다.

## 허브 데이터베이스 구조

| 컬렉션 | 문서 id | 누가 쓰나 | 내용 |
|---|---|---|---|
| `issues` | 주차 (예: `2026-W48`) | 메인 작업 | 호 본문 (`prepare_issue.py`가 만든다) |
| `figures` | `<주차>-f1`, `<주차>-e1` | 메인 작업 | 그림·수식 SVG |
| `feedback` | 주차 | 페이지 (사용자 평가) | `ratings` {섹션 번호 또는 `summary`: 1~5}, `comments` {같은 키: 섹션별 코멘트}, `answers` {질문 id: 답}, `comment` (전체 의견) |
| `feedback_tags` | 주차 | 페이지 (반응 버튼) | `tags` {항목 id: [`up`, `known`, `deeper`, `wrong`, `meh`] 중 누른 것} |
| `ledger` | `<주차>--<출처>--<대상>` | 메인 작업 | 피드백 원장: 원문 한 건씩 (형식은 작업 프롬프트) |
| `experiments` | `X<번호>` | 메인 작업 | 변경 하나하나의 가설과 판정 |
| `chatlog` | `<주차>--<프로젝트 slug>` | 채팅 수집 작업 | 프로젝트 대화 요약 |
| `cclog` | `<주차>--<호스트>` | Claude Code 수집 작업 | Claude Code 세션 요약 |
| `prefs` | `main` | 메인 작업 | `profile` (원장에서 계산한 선호), `rules` |
| `skill` | `guide`, `figstyle` | 메인 작업 | 살아 있는 가이드와 그림 코드 최신본 |
| `skill_history` | `<이름>-v<번호>` | 메인 작업 | 고치기 전 버전 (되돌리기용) |
| `prompts` | `main`, `cc-collector`, `chat-collector` | 사용자 (채팅에서 Claude가 대신 고침) | 스케줄 작업이 매번 읽는 지시문. 작업은 고치지 않는다 |

`issues`와 `figures` 말고는 모두 소유자만 읽을 수 있다. 페이지를 공유해도 보이지 않는다.

## issue.json 형식

```json
{
  "week": "2026-W47",
  "title": "주장 한 문장",
  "keywords": ["키워드"],
  "applied_feedback": "지난 피드백 반영 1~2줄 (없으면 생략)",
  "corrections": ["정정 한 줄 (없으면 생략)"],
  "summary_heading": "한눈에 보기의 제목 (주장형)",
  "summary": ["문단", "문단"],
  "cards": [{"value": "약 44%", "label": "짧은 라벨", "note": "출처와 설명 (1-B)"}],
  "sections": [{"num": "1-A", "label": "기반 논문", "heading": "주장형 제목", "blocks": []}],
  "references": [{"authors": "Bay, Y. Y., & Yearick, K. A.", "year": "2026", "title": "...", "url": "https://...", "venue": "arXiv:2607.00152"}],
  "items": {"1-B.1": {"kind": "paper", "title": "짧은 이름", "topics": ["RL", "GRPO"], "venue": "MLSys 2025", "level": "기초|중급|심화"}},
  "questions": [{"id": "Q1", "text": "확인하고 싶은 것", "options": ["선택지", "선택지"]}],
  "monthly_review": []
}
```

`week`는 발행일(토요일, 한국 시간)의 ISO 주차다. 완성된 예시는 `references/example-issue.json`에 있다 (디자인 확인용 샘플이라 `"sample": true`가 붙어 있다. 실제 호에는 넣지 않는다). 처음 만들 때 한 번 읽고 톤과 밀도를 맞춘다. `items`에는 반응을 받을 항목(논문, 뉴스, 그림 등)을 등록하고, 해당 블록에 `"item": "<id>"`를 붙인다. `paper`와 `figure` 블록은 반드시 item이 있어야 하고(검사 스크립트가 확인한다), 뉴스는 항목마다 `p` 블록 하나로 쓰고 item을 붙인다. 페이지는 item이 붙은 블록 아래에 반응 버튼을 그린다. kind는 paper, news, figure, concept, tip, other 중 하나이고, topics·venue·level은 나중에 어떤 내용이 맞는지 분석할 때 쓰이니 성실히 채운다. `questions`는 해석이 갈리는 피드백을 확인할 때만 쓰고 호당 2개 이내다 (id는 Q1, Q2). `monthly_review`는 매월 첫 호에만 블록 목록으로 채운다. 목차와 피드백 영역은 페이지가 `sections`에서 자동으로 만든다.

블록 종류 (본문 텍스트는 `**굵게**`, `` `코드` ``, `[텍스트](https://…)`를 지원):

| type | 필드 | 쓰임 |
|---|---|---|
| `p` | text | 일반 문단 |
| `h2` | text | 하위 제목, 예: "1-B.1 ..." |
| `bullets` | items | 짧은 목록 |
| `quote` | label, text | "계기": 내 세션 발언 인용 |
| `paper` | title, url, venue, affil, exception | 논문 정보. 예외 항목이면 exception에 이유 |
| `figure` | path, caption | 그림 (번호 자동) |
| `equation` | path | `fs.equation`으로 만든 수식 |
| `code` | lines | 15줄 이내 골격 코드, 자리표시는 `# [여기에 X]` |
| `callout` | title, items 또는 text, tone("warm" 선택) | 체크리스트, 읽을 곳·복습 질문 |
