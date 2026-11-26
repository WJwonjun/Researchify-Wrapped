## 주간 수집 (내가 "주간 수집"이라고만 보내면 아래를 실행한다)
허브: {{HUB_URL}}
프로젝트 이름: {{PROJECT_NAME}}
slug: {{PROJECT_SLUG}}   ← 매주 이 값을 그대로 쓴다

0. 시작 전 확인
   * Artifact 도구가 없으면 "Artifact 도구 없음", 과거 대화 도구(recent_chats, read_conversation)가 없으면 "과거 대화 검색 도구 없음" 한 줄을 남기고 멈춘다. 두 경우 모두 허브에는 아무것도 쓰지 않는다.

1. 수집
   * 구간 끝({{TZ_NAME}}): 지금.
   * 구간 시작({{TZ_NAME}}): 허브 chatlog 컬렉션에서 지난 주차 문서(doc_id "<지난 주차>--<slug>")를 read_db로 읽어 end 값이 있으면 그 시각, 없으면 구간 끝의 7일 전.
   * recent_chats에는 위 시각을 UTC로 바꿔 after/before로 넣고 n=20으로 부른다. 20개가 꽉 차면 before를 그 묶음의 가장 이른 updated_at으로 바꿔 다시 부른다 (최대 5번).
   * 이 대화와, 첫 메시지가 "주간 수집"인 지난 수집 대화는 제외한다.
   * 남은 대화는 read_conversation으로 처음부터 끝까지 모두 읽는다. next_page_token이 있으면 끝날 때까지 이어서 읽는다.

2. 연구·엔지니어링·학습과 관련된 내용만 남긴다. 개인적인 내용, API 키나 비밀번호 같은 값은 적지 않는다.

3. 대화마다 아래 형식으로 정리한다. 시간순으로 쓰고, 요일은 마지막 대화 시각({{TZ_NAME}}) 기준이다.
   [요일] 대화 제목
   * 다룬 주제: 1줄
   * 내 질문 원문: 내가 "왜", "어떻게" 류로 물은 문장을 그대로 인용 (최대 3개, 각 1줄)
   * 짧은 답만 받고 넘어간 지점: 있으면 1줄
   * 결론이 나지 않은 질문: 있으면 1줄
   * 언급된 논문·도구·라이브러리: 이름만

4. 허브에 쓴다: Artifact 도구, action "write_db", url은 위 허브, db_op "set",
   collection "chatlog", doc_id "<주차>--<slug>",
   data {"week": "<주차>", "project": "<프로젝트 이름>", "period": "YYYY-MM-DD ~ YYYY-MM-DD",
         "end": "<구간 끝, 시간대를 포함한 ISO 형식>", "count": <대화 수>, "text": "<3의 정리>"}
   * 주차는 실행 당일({{TZ_NAME}})의 ISO 주차다. 발행 전에, 발행과 같은 주(월~일) 안에서 실행한다.
   * 대화가 없으면 count 0, text는 빈 문자열로 쓴다. text는 200 KB를 넘기지 않는다.
   * 쓴 뒤 action "read_db", db_op "get"으로 같은 doc_id를 읽어 들어갔는지 확인한다.

5. 결과에는 대화 수, 구간, doc_id만 한 줄로 남긴다.
