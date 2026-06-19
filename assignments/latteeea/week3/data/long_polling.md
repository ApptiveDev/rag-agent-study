### 요구사항 및 구현

요구사항 : 기기/서버 점검 중이라는 창을 키오스크에 띄워야 하고 이는 관리자웹에서 제어 가능해야함

기술적 고민 : polling vs long polling vs websocket

- 프론트와 백 서버가 주기적으로 통신할 수 있는 것은 크게 세 가지가 있고 각각의 장단점을 보면
    - polling : N초마다 요청 ↔ 요청 받는 즉시 응답 / N초만큼 지연되고 트래픽과 쿼리가 반복됨
    - long polling : 클라이언트가 요청 → 서버가 ‘변화가 생길 때까지’ 응답을 안 하고 대기, 변화가 생기면 즉시 응답 → 클라이언트는 응답 받자마자 바로 다음 long - polling 요청을 다시 걸기 / **동시 접속자가 많으면 ‘열려 있는 요청’이 계속 쌓임 (그때는 이 단점을 미처 파악하지 못했고 이 문제로 인해 서버가 종료되는 사건 발생)**
    - websocket : 연결 1개를 계속 유지하면서 push → 찐 실시간 / 인프라 쪽에서 신경쓸 게 좀 있음 무거우니까
- 채팅 같은 곳에서나 쓰이는 게 websocket인데 기기 점검 여부에 대해 표시하기 위해 연결을 하나 아예 열어두는 건 너무 투머치이다. 왜냐면 거의 쓰지 않는 기능이기 때문에. 근데 일단 그 여부가 수정되면 최대한 빠르게 바뀌는 게 좋다. 간격이 1분을 넘어가진 않았으면 좋겠다 → Long Polling 결정

### 문제 상황

```c
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/protocols/http/httptools_impl.py", line 416, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/applications.py", line 1135, in __call__
    await super().__call__(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 115, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 101, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 355, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 243, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/app/apis/endpoints/system_status.py", line 183, in poll_system_status
    new_statuses = query.order_by(models.SystemStatus.created_at.desc()).all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2704, in all
    return self._iter().all()  # type: ignore
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2857, in _iter
    result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
                                                  ~~~~~~~~~~~~~~~~~~~~^
        statement,
        ^^^^^^^^^^
        params,
        ^^^^^^^
        execution_options={"_sa_orm_load_options": self.load_options},
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 2351, in execute
    return self._execute_internal(
           ~~~~~~~~~~~~~~~~~~~~~~^
        statement,
        ^^^^^^^^^^
    ...<4 lines>...
        _add_event=_add_event,
        ^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 2239, in _execute_internal
    conn = self._connection_for_bind(bind)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 2108, in _connection_for_bind
    return trans._connection_for_bind(engine, execution_options)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in _connection_for_bind
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/state_changes.py", line 137, in _go
    ret_value = fn(self, *arg, **kw)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1187, in _connection_for_bind
    conn = bind.connect()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 3285, in connect
    return self._connection_cls(self)
           ~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 143, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 3309, in raw_connection
    return self.pool.connect()
           ~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 447, in connect
    return _ConnectionFairy._checkout(self)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 1264, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 711, in checkout
    rec = pool._do_get()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/impl.py", line 166, in _do_get
    raise exc.TimeoutError(
    ...<4 lines>...
    )
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)
2026-01-30 12:30:29,926
```

## 제미나이 정리본 (참고)

### 1. 도입: 왜 Long Polling을 선택했는가?

- 실시간성 데이터 업데이트가 필요했고, WebSocket 도입 비용 대비 효율적인 Long Polling을 선택했다.

### 2. 위기: 트래픽 증가와 서버 다운

- 클라이언트 수가 늘어나자 서버 리소스가 급증하며 프로세스가 Kill 되는 현상 발생.

### 3. 원인 파악 (이 부분이 핵심!)

- AI(커서)가 생성해 준 코드는 **'기능적 구현'**에만 충실했을 뿐, **'동시 접속자 수에 따른 커넥션 유지 비용'**이나 **'타임아웃 처리'**가 미흡했음을 발견.
- 구체적으로 어떤 코드 라인이 무한 대기를 유발했거나 메모리 누수를 일으켰는지 분석.

### 4. 해결 및 개선

- 서버가 요청을 무한정 붙잡지 않도록 `Max Timeout` 설정.
- 비어있는 응답을 보낼 때의 오버헤드 최적화.
- (만약 했다면) Node.js의 경우 Event Loop가 차단되지 않도록 비동기 로직 수정.

---

## 💡 "AI만 쓰는 사람"처럼 안 보이려면?

글 마무리나 중간에 이런 뉘앙스를 한 줄만 섞어주세요.

> "AI는 구현 속도를 비약적으로 높여주지만, 시스템의 안정성과 확장성(Scalability)은 결국 개발자가 도메인 지식을 바탕으로 검증해야 한다는 것을 깨달았다."
> 

| **지표 (Metrics)** | **수정 전 (AS-IS)** | **수정 후 (TO-BE)** | **개선 결과** |
| --- | --- | --- | --- |
| **최대 동시 접속 수** | 약 30 ~ 40명 | 200명 이상 테스트 통과 | **500% 향상** |
| **평균 메모리 사용량** | 800MB (임계치 도달) | 250MB (안정권) | **68% 감소** |
| **장애 발생 주기** | 1일 3~4회 강제 종료 | 장애 발생 없음 | **안정성 확보** |

### 임시 트러블슈팅

- 문제 : 키오스크 기기 하나 매장에 더 들어갔는데 몇 분 안돼서 서버가 강제 종료됨 (아무것도 이용 불가;;)
- 원인 : 관리자웹에서 기기/서버 점검 창을 키오스크 기기에 띄울 수 있도록 하는 기능을 long-polling 으로 구현했었는데 이걸 사용하는 기기가 하나 더 늘어나니가 db 점유율이 너무 많아져서 그런 것.
    - long-polling + SQLAlchemy Session이 커넥션을 오래 물고 있었음
        - long-polling 이 트랜잭션으로 작동되는데 session이 처음 db 작업을 하는 순간 트랜잭션이 자동 시작되고 그 트랜잭션/커넥션이 commit/rollback/close 되기 전까지 풀에 안 돌아가 버리는 케이스임. (긴 요청에 while로 계속 도는거지)
        - 폴링 요청이 여러 개 동시에 걸려버리면 session 1개씩 + 커넥션 1개씩 장시간 점유 → 풀 고갈 → QueuePooltimeout 이 터짐
- 해결
    - check_interval 1s → 3s
        - 폴링 간격을 1초 → 3초로 늘렸음
    - pool_size/overflow 키우기 땜빵용으로
        - 동시 커넥션 한도 늘려서 조금 더 버티게 하기
    - 하지만 long - polling 요청이 커넥션을 너무 오래 점유하면 pool_size를 키워도 언젠가 또 고갈남 (클라이언트 수가 늘수록 선형적 증가)
    - **근본적으로 끝내려면 long - poll 루프에서 매번 트랜잭션을 끝내서 커넥션 반환**

## 타겟 트러블슈팅

원인: 임시로 동시 커넥션 제한 수 늘린 것 안정적으로 고치기

문제: long polling 구현 방식이 db 커넥션 풀과 궁합이 좋지 않음

- 일단 기본적으로 사용하는 리소스 양은 long polling > websocket임
- websocket을 안 쓰고 long polling 을 사용한 이유가 websocket 같이 연결 하나를 아예 열어두고 있을만한 기능이 아니라고 생각함. 별로 바뀌는 게 잦지 않고 매우 드문 거고 1분 이상의 간격으로 요청하기에는 변경이 일어날 시 빠르게 알아차리는 게 중요하다고 생각해서 long polling 을 한건데 long polling 을 사용하는 기기가 여러개라면 어쩌면 websocket보다 그 리소스 잡아먹는 양이 더 안좋을수도 있는 것임.
- 즉, 데이터 변경이 드문 기능이라서 효율적일 줄 알았으나, HTTP 오버헤드의 반복, 동시 접속자 수 비례 리소스 점유 라는 치명적인 단점이 트래픽 증가 시점에 서버 다운이라는 결과로 이어짐

해결 : SSE를 써도 되긴 하나 기기 갯수가 제한되어 있기 때문에 long polling 을 제대로 쓰는 쪽으로 해보자

### system-status 로그가 계속 찍히는 이유

클라이언트가 응답을 받자마자 즉시 재요청하고, 서버가 실제로는 바로 응답해버림 → since가 매번 None으로 들어옴 → 즉시 전체 반환하는 분기 

→ since가 실제로 들어오는지 확인 (None으로 들어와서 값 넣어주는 걸로 했더니 바로 로그 갯수 확연히 줄어들음 → 1초에 6개씩은 나오던게 6초에 3개 정도 나온다)

### 정상적인 long polling 방식

⇒ ‘”대기 동안의 비용이 거의 0 이어야 한다.”

long polling 요청이 오래 살아있으니까 서버 리소스는 기본적으로 더 사용하게 됨(열려있는 http 요청 자체가 서버 자원을 먹음). 특히 스레드/커넥션 풀 같은 제한이 있으면 클라이언트 수에 비례해서 항상 떠있는 요청 수가 늘어나는 것. → 변경이 드물어도 long polling 이 cheap 하지 않을 수 있다 

⇒ 보통 점검 상태 같은건 서버 → 클라이언트 단방향 push 인 SSE를 많이 사용한다. 

### 효율을 나눠서 보기

1. 네트워크/HTTP 오버헤드
    1. polling : 주기마다 요청/응답 반복 → 오버헤드 일정하게 발생
    2. long polling : 요청 오래 열려있다가 timeout 때만 재요청 → 요청 횟수 줄어들고 변경이 매우 드물면 요청 수 확실히 줄음 
2. 서버 리소스 (이게 제일 중요)
    1. polling : 요청은 짧게 끝남 → 동시 요청 수 낮고 예측 가능
    2. long polling : 항상 열려있는 요청이 클라이언트 수만큼 발생 → 동시 요청 수가 클라이언트 수와 거의 동일하게 유지
    
    ⇒ polling이 유리함 (커넥션/메모리/서버 워커 관점에서)
    
3. DB 부하 
    1. polling : 주기마다 DB 조회 → 변경 없어도 쿼리 계속
    2. long polling : 구현에 따라 다른데
        1. 나쁜 구현(내 코드) : polling이랑 똑같이 쿼리 계속
        2. 좋은 구현(이벤트 기반) : 변경 발생 시에만 DB 조회 → DB 부하 극적으로 줄어듦 
    
    ⇒ DB 측면에서 이득을 보려면 이벤트 기반에 가까워야 한다. 
    

### 내 상황에서는 뭐가 효율적이냐?

1. 3~10초 polling 
    1. 클라이언트가 3~10초마다 최신 상태 요청
    2. 즉시성은 떨어지지만
    3. 서버는 요청 짧고 안정적이어서 좋음
    4. DB도 인덱스 + latest 같은 endpoint로 최적화하면 ㄱㅊ 
2. SSE (보통 점검 상태는 이걸 사용)
    1. websocket처럼 양방향/복잡하지 않음
    2. HTTP 기반 단방향 스트림이므로 투머치 느낌 덜하고
    3. 서버가 변경시점에만 push 하면 됨
    4. long polling 보다 열려있는 연결을 효율적으로 다루는 편 
3. long polling 유지하되 **제대로** 만들기 
    1. 매 반복마다 DB 세션을 닫거나 rollback 해서 커넥션을 반환
    2. 가능하면 DB 폴링을 줄이고 캐시/이벤트 사용
    3. 동시 접속자 증가에 따라 열린 요청 수는 늘어나긴 함 (본질적)