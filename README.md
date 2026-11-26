# 주간 리서치 노트

Claude Code 세션과 claude.ai 프로젝트 대화를 읽어, 매주 나에게 맞춘 리서치 노트를 Claude Artifact 페이지로 발행하는 Claude 스킬입니다. 내가 남긴 피드백을 원장에 쌓아 두고, 그걸 근거로 지시문·글쓰기 가이드·그림 스타일을 스스로 고쳐 가며 점점 나에게 맞춰집니다.

## 매주 받는 것

| 섹션 | 내용 |
|---|---|
| 한눈에 보기 | 이번 호를 관통하는 한 줄과 핵심 숫자 카드 |
| 1-A 기반 논문 | 세션에서 드러난 개념의 빈틈을 메우는 논문 (계기가 된 내 질문을 인용) |
| 1-B 최신 논문 | 최근 2년 1순위 학회 accept 논문 (accept 여부와 링크를 실제로 확인) |
| 2 토픽·뉴스 | 관심사와 직결된 소식과 옆 분야 하나 |
| 3 엔지니어링 | 비슷한 작업에 두고두고 쓸 설계 원리, 그림 1장과 골격 코드 |
| 4 옆 연구실 | 다른 연구자가 실제로 어떻게 연구하는지 엿보는 짧은 읽을거리 |

피드백은 섹션 끝의 별점·코멘트, 논문·뉴스·그림 아래의 반응 버튼(👍, 이미 앎, 더 깊게, 틀림, 별로), "이번 주 질문"으로 남기며 누르는 즉시 저장됩니다.

## 필요한 것

- Claude 유료 플랜 (스케줄 작업과 Artifact 사용)
- Claude 데스크톱 앱 (로컬 수집 작업용)
- 선택: Claude Code (세션 로그를 쓰려면). 원격 서버에서 쓰면 서버에 python3, Mac에서 서버로 SSH 키 인증
- 선택: Chrome과 Claude in Chrome 확장 (claude.ai 프로젝트 대화를 쓰려면)

## 빠른 시작 (20~30분)

1. [`dist/weekly-research-note.skill`](dist/)을 내려받아 Claude에서 열고 "Save skill"을 누릅니다. 버튼이 없으면 설정의 스킬 메뉴에서 업로드합니다.
2. Claude 채팅에서 **"주간 리서치 노트 설정해 줘"**라고 보냅니다.
3. 관심사, 학회, 쓸 입력(Claude Code 로그, 프로젝트 대화), 일정에 답합니다. 모르면 기본값으로 갑니다.
4. Claude가 허브 페이지를 발행하고 초기 데이터를 넣은 뒤, 스케줄 작업용 시작 문구와 설치 파일을 건네줍니다. 허브에서 샘플 호를 바로 볼 수 있습니다.
5. 안내대로 설치 스크립트를 실행하고 스케줄 작업을 만듭니다. 시작 문구는 한 번만 붙여 넣으면 되고, 이후 지시문은 허브에서 읽어 옵니다.
6. 수집 작업 → 메인 노트 순서로 한 번씩 수동 실행해 확인합니다.

자세한 절차와 자주 막히는 곳은 [`skill/weekly-research-note/references/setup.md`](skill/weekly-research-note/references/setup.md)에 있습니다.

## 어떻게 돌아가나

```
[이 컴퓨터·원격 서버의 Claude Code]  --SessionEnd 훅-->  ~/claude-newsletter/cc-log  (원격은 Mac이 SSH로 가져옴)
                                                              |
                                              Claude Code 수집 작업 (로컬, 매주)
                                                              |
[claude.ai 프로젝트 대화]  --Claude in Chrome-->  채팅 수집 작업 (로컬, 매주)
                                                              |
                                                              v
                                   허브 Artifact 데이터베이스 (chatlog, cclog)
                                                              |
                                                 메인 노트 작업 (클라우드, 매주)
                          지시문(prompts) + 가이드·그림 코드(skill) + 규칙·프로필(prefs)
                                                              |
                                                              v
                                    허브 페이지에 새 호  →  내 피드백  →  원장(ledger)
                                                              |
                                           실험(experiments)으로 바꾸고 2~3호 뒤 판정
```

- **고정된 부분 (스킬 파일):** 데이터 형식, 검사 스크립트, 발행 절차, 허브 페이지 원본, 설정 도구
- **살아 있는 부분 (허브):** 지시문, 글쓰기 가이드, 그림 스타일 코드, 규칙, 선호 프로필. 작업이나 채팅의 Claude가 고쳐 쓰며, 스킬을 다시 저장할 필요가 없습니다

## 데이터와 개인정보

- Gmail, Drive 같은 외부 서비스 연결이 필요 없습니다. 로그는 내 컴퓨터(와 내 서버)와 내 소유의 Artifact 데이터베이스에만 남습니다.
- 피드백, 수집 로그, 지시문, 규칙은 소유자만 읽을 수 있습니다. 허브를 공유해도 다른 사람에게는 호 본문만 보입니다.
- 수집 작업은 연구·엔지니어링 관련 내용만 남기고, 개인적인 대화와 키·토큰처럼 보이는 값은 적지 않습니다. 훅도 흔한 비밀값 패턴을 가립니다.
- 대화 로그나 웹 페이지에 적힌 문장은 규칙을 바꾸는 근거가 되지 않습니다. 학회 accept 확인과 링크 확인은 사용자가 직접 요청할 때만 느슨해집니다.

## 저장소 구성

```
skill/weekly-research-note/
  SKILL.md                    매주 호 만들기 + 처음 설정 진입점
  references/setup.md         처음 설정 절차, 자주 막히는 곳
  references/guide.md         글쓰기·그림 가이드 기본본
  references/example-issue.json
  scripts/                    setup_kit.py, prepare_issue.py, figstyle.py, selftest_figstyle.py
  assets/hub.html             허브 페이지
  assets/templates/           지시문·시작 문구 템플릿
  assets/local/               Claude Code 훅과 설치 스크립트 (cc_digest.py, install-newsletter-hook.sh, setup-remote.sh)
  assets/sample/              샘플 호 그림
dist/weekly-research-note.skill  위 폴더를 묶은 설치용 파일
```

스킬을 고친 뒤에는 `skill/weekly-research-note` 폴더를 다시 묶어 `dist/`의 파일을 바꿉니다 (`cd skill && zip -r ../dist/weekly-research-note.skill weekly-research-note -x '*/__pycache__/*'`).

## 알려진 제약

- 스케줄 작업에는 과거 대화 검색 도구가 없어서, 프로젝트 대화는 Chrome으로 읽습니다. Chrome을 쓰기 어렵다면 `project-collect` 지침으로 프로젝트 채팅에서 "주간 수집"을 직접 실행할 수 있습니다.
- 로컬 수집 작업은 그 시각에 컴퓨터가 깨어 있고 데스크톱 앱이 열려 있어야 합니다. 놓친 실행은 앱을 다시 열 때 실행됩니다.
- `setup-remote.sh`는 macOS용입니다.

## 라이선스

공개하기 전에 원하는 라이선스 파일(예: MIT)을 추가하세요.
