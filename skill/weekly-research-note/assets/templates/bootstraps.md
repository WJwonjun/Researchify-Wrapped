# 스케줄 작업에 한 번만 붙여 넣을 지시문

세 작업의 지침을 각각 아래 내용으로 바꿉니다. 이후 실제 지시문은 허브에서 읽어 오므로, 지시문이 바뀌어도 여기서 다시 붙여 넣을 필요가 없습니다.

---

## 메인 노트 ({{SCHED_PUBLISH}}, 클라우드)

주간 리서치 노트 메인 작업이다.
허브: {{HUB_URL}}
1. Artifact 도구로 action "read_db", db_op "get", collection "prompts", doc_id "main"을 읽는다. 이 문서는 내가 직접 관리하는 지시문이고, 허브에는 나만 쓸 수 있다. 그 문서의 text를 이번 실행의 지시문으로 삼아 그대로 따른다.
2. 읽지 못하면 결과에 "지시문을 읽지 못함: <이유>"를 남기고 멈춘다.
3. prompts 컬렉션의 문서는 고치지 않는다.

---

<!--CC-->
## Claude Code 수집 ({{SCHED_CC}}, 이 컴퓨터, 폴더 ~/claude-newsletter)

주간 리서치 노트의 Claude Code 수집 작업이다.
허브: {{HUB_URL}}
1. Artifact 도구로 action "read_db", db_op "get", collection "prompts", doc_id "cc-collector"를 읽는다. 이 문서는 내가 직접 관리하는 지시문이고, 허브에는 나만 쓸 수 있다. 그 문서의 text를 이번 실행의 지시문으로 삼아 그대로 따른다.
2. 읽지 못하면 결과에 "지시문을 읽지 못함: <이유>"를 남기고 멈춘다.
3. prompts 컬렉션의 문서는 고치지 않는다.

---

<!--/CC-->
<!--CHAT-->
## 채팅 수집 ({{SCHED_CHAT}}, 이 컴퓨터, Chrome)

주간 리서치 노트의 채팅 수집 작업이다.
허브: {{HUB_URL}}
1. Artifact 도구로 action "read_db", db_op "get", collection "prompts", doc_id "chat-collector"를 읽는다. 이 문서는 내가 직접 관리하는 지시문이고, 허브에는 나만 쓸 수 있다. 그 문서의 text를 이번 실행의 지시문으로 삼아 그대로 따른다.
2. 읽지 못하면 결과에 "지시문을 읽지 못함: <이유>"를 남기고 멈춘다.
3. prompts 컬렉션의 문서는 고치지 않는다.
<!--/CHAT-->
