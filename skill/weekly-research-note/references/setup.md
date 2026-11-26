# 처음 설정 (Claude 채팅에서 한 번)

사용자가 "주간 리서치 노트 설정해 줘", "뉴스레터 세팅" 같은 요청을 하면 이 문서를 따른다. Artifact 도구와 코드 실행이 있는 Claude 채팅에서 진행한다. 끝나면 사용자에게는 스케줄 작업 몇 개를 만드는 일만 남는다.

## 1. 물어보기

한 번에 묻고, 답이 없으면 기본값을 쓴다. 선택형 질문 도구가 있으면 그것으로 묻는다.

- 연구 관심사 한두 줄 (로그가 적은 주에 기준이 된다)
- 1순위 학회. 기본값은 ML: NeurIPS, ICML, ICLR / Systems: OSDI, NSDI, SOSP, ASPLOS, MLSys, MobiSys
- 예외로 받을 기관. 기본값은 MIT, Stanford, UC Berkeley, CMU, UW, Google DeepMind, Meta, Microsoft Research, NVIDIA
- 입력으로 쓸 것
  - Claude Code 로그: 이 컴퓨터에서 쓰는지, 원격 서버에서 쓰는지 (서버 이름은 나중에 스크립트 실행 때만 필요)
  - claude.ai 프로젝트 대화: 쓴다면 대상 프로젝트 이름. slug는 Claude가 영문 소문자·숫자·밑줄·하이픈으로 제안한다
- 시간대와 일정. 기본값은 한국 시간, Claude Code 수집 금요일 22:00, 채팅 수집 금요일 22:30, 발행 토요일 09:00. 수집은 발행과 같은 주(월~일) 안에서 발행보다 먼저여야 한다 (호 이름이 ISO 주차라서)

## 2. 허브 발행

1. `python <skill>/scripts/setup_kit.py capabilities`의 출력을 capabilities로 쓴다.
2. `<skill>/assets/hub.html`을 출력 폴더(예: `/mnt/user-data/outputs/weekly-research-note.html`)로 복사한다.
3. Artifact `action: "publish"`로 발행한다. title "주간 리서치 노트", favicon "📓", 위 capabilities. 받은 주소가 hub_url이다.

## 3. 초기 데이터

1. 아래 형식으로 `config.json`을 쓰고 `python <skill>/scripts/setup_kit.py render config.json out`을 실행한다. "고칠 것"이 나오면 고친다.
2. Artifact `action: "write_db"`, `url: hub_url`, `db_op: "batch"`, `writes: <out/writes.json의 내용>`.
3. `read_db`로 `prompts/main`이 들어갔는지 확인한다. 이제 허브에 샘플 호가 보인다.

```json
{
  "hub_url": "https://claude.ai/artifact/...",
  "interests": "LLM 서빙, 분산 학습 통신",
  "tz_name": "한국 시간(UTC+9)",
  "tier1_ml": ["NeurIPS", "ICML", "ICLR"],
  "tier1_sys": ["OSDI", "NSDI", "SOSP", "ASPLOS", "MLSys", "MobiSys"],
  "exception_orgs": ["MIT", "Stanford"],
  "projects": [{"name": "claude.ai에 보이는 프로젝트 이름", "slug": "my-project"}],
  "sources": {"claude_code": true, "chat": true},
  "schedule": {"cc": "매주 금요일 22:00", "chat": "매주 금요일 22:30", "publish": "매주 토요일 09:00"}
}
```

## 4. 건넬 것

present_files로 `out/bootstraps.md`, `out/local/`의 파일들(Claude Code 수집을 켰을 때), `out/project-collect/`의 파일들(채팅 수집을 켰을 때, 예비용)을 건네고 허브를 연다(Artifact `action: "open"`). 그다음 아래 안내를 사용자 말투에 맞게 전한다.

## 5. 사용자가 할 일 (안내문)

1. **설정:** 코드 실행 및 파일 생성 기능을 켠다. 일과 개인 대화가 섞이는 게 싫으면 메모리를 끈다.
2. **허브:** 허브 주소를 북마크하고 샘플 호를 본다.
3. **Claude Code 로그 (켰을 때):** 받은 `local` 파일들을 한 폴더에 둔다.
   - 이 컴퓨터에서 Claude Code를 쓰면: `bash install-newsletter-hook.sh`
   - 원격 서버에서 쓰면 (Mac에서): `bash setup-remote.sh 서버1 서버2 ...`. 서버 로그를 하루 네 번과 금요일 21:55에 가져온다 (시각은 스크립트 안에서 바꿀 수 있다)
4. **앱:** 로컬 작업용으로 Claude 데스크톱 앱을 설치한다. 채팅 수집을 켰으면 Chrome에 Claude in Chrome 확장도 설치하고 claude.ai에 로그인해 둔다.
5. **스케줄 작업:** `bootstraps.md`의 문구를 지침으로 넣어 만든다.
   - 메인 노트: 클라우드에서 실행 (컴퓨터가 꺼져 있어도 발행된다)
   - Claude Code 수집: 데스크톱 앱에서 만들고 작업 폴더를 `~/claude-newsletter`로 지정한다 (폴더를 지정해야 이 컴퓨터에서 돈다)
   - 채팅 수집: 데스크톱 앱에서 만들고 이 컴퓨터에서만 실행되게 한다 (Require this computer, 또는 작업 폴더 지정)
   - 권한은 자동 승인. 첫 수동 실행에서 묻는 권한은 "always allow"
6. **첫 실행:** Claude Code 수집 → 채팅 수집 → 메인 노트 순서로 수동 실행하고 각 결과의 마지막 줄을 확인한다. 첫 정식 호가 나오면 샘플 호는 자동으로 지워진다.
7. **매주:** 허브에서 읽고, 섹션 끝 평가·항목 반응·질문 답을 남긴다. 누르면 바로 저장된다.

## 자주 막히는 곳

| 증상 | 원인과 해결 |
|---|---|
| "과거 대화 검색 도구 없음" | 스케줄 작업에는 과거 대화 도구가 없다. Chrome 채팅 수집을 쓰거나, `project-collect` 지침을 프로젝트 지침에 넣고 프로젝트 채팅에서 "주간 수집"이라고 보낸다 |
| "Chrome 사용 불가" | 작업이 클라우드에서 돌았다. 이 컴퓨터에서 실행되도록 설정한다 |
| 폴더 접근 거부 | 작업 설정에서 `~/claude-newsletter` 폴더를 추가한다 |
| "지시문을 읽지 못함" | 허브 주소 오타이거나 3단계가 빠졌다 |
| 원격 서버 가져오기 실패 | 키 인증(`ssh-copy-id`), 키 암호를 키체인에 저장, VPN 확인. `~/claude-newsletter/last-pull.txt`에 결과가 남는다 |

## 이후 바꾸기

지시문을 바꾸고 싶다는 요청을 받으면 허브의 `prompts/<main|cc-collector|chat-collector>`를 읽어 고친 뒤 write_db로 쓴다 (`version` 필드 +1, `updated` 갱신, 읽을 때 받은 문서 version을 if_version으로). 스케줄 작업에 다시 붙여 넣을 필요는 없다. 피드백에서 작업이 배우는 것은 따로 rules, 가이드, 그림 코드, 실험으로 쌓인다.
