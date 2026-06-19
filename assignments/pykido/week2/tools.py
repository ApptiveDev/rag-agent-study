from langchain_core.tools import tool


PROBLEMS: dict[str, dict] = {
    "pgs-43238": {
        "id": "pgs-43238",
        "title": "입국심사",
        "platform": "Programmers",
        "level": "Lv.3",
        "topics": ["binary-search"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/43238",
        "description": (
            "n명과 각 입국 심사대 처리 시간 times[]가 주어질 때, 모두 심사하기 위한 최소 시간을 구하는 문제. "
            "답이 시간 t에 대해 단조 → parametric binary search."
        ),
        "reference_approach": (
            "f(t) = sum(t // x for x in times)는 t에 대해 단조 증가. f(t) >= n 인 최소 t를 이분 탐색."
        ),
        "reference_complexity": "O(M log(max(times) * n)), M = len(times)",
        "key_checkpoints": [
            "lo=1, hi=max(times)*n 으로 범위를 충분히 크게",
            "단조성을 명시 (시간↑ → 처리 인원↑)",
            "f(mid) >= n 일 때 hi=mid-1 (lower bound)",
        ],
        "common_pitfalls": [
            "lo=0 이면 무한 루프",
            "hi=max(times) 만 두면 사람 수 많을 때 답 못 찾음",
            "O(N) 선형 탐색은 N=10^9 스케일에서 TLE",
        ],
    },
    "pgs-43236": {
        "id": "pgs-43236",
        "title": "징검다리",
        "platform": "Programmers",
        "level": "Lv.4",
        "topics": ["binary-search"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/43236",
        "description": "바위 좌표가 주어지고 n개를 제거할 수 있을 때 가장 짧은 점프 거리의 최댓값. parametric search.",
        "reference_approach": "최소 점프 거리 d 이분 탐색. f(d) = 거리 d 미만이 되는 인접 쌍을 그리디 제거 횟수.",
        "reference_complexity": "O(R log(distance)), R = len(rocks)",
        "key_checkpoints": [
            "바위 정렬",
            "제거 시뮬레이션을 그리디로 (마지막 위치 추적)",
            "upper bound 형태 — 답=lo-1 또는 hi 처리",
        ],
        "common_pitfalls": [
            "distance 배열을 정렬하는 잘못된 접근 (단조성 깨짐)",
            "d 범위를 좌표값이 아닌 인덱스로 잡음",
        ],
    },
    "pgs-43165": {
        "id": "pgs-43165",
        "title": "타겟 넘버",
        "platform": "Programmers",
        "level": "Lv.2",
        "topics": ["bfs-dfs"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/43165",
        "description": "각 원소 앞에 +/-를 붙여 target을 만드는 경우의 수. DFS/백트래킹 입문.",
        "reference_approach": "각 i에서 +/- 이진 분기 DFS. i==len 도달 시 누적합==target 검사.",
        "reference_complexity": "O(2^N)",
        "key_checkpoints": [
            "base case (i == len(numbers))",
            "+ 와 - 두 분기 모두 호출",
            "DP 메모이제이션 ((i, sum)) 도 가능",
        ],
        "common_pitfalls": [
            "DFS를 BFS로 짜며 메모리 폭발",
            "누적합을 list append/pop 부수효과로",
        ],
    },
    "pgs-118667": {
        "id": "pgs-118667",
        "title": "두 큐 합 같게 만들기",
        "platform": "Programmers",
        "level": "Lv.2",
        "topics": ["two-pointers", "queue"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/118667",
        "description": "두 큐 합을 같게 만드는 최소 작업 횟수. pop/insert를 두 포인터처럼.",
        "reference_approach": "deque 1개로 합쳐 보고 합이 큰 쪽에서 pop → 작은 쪽에 push. 종료 상한 4*N.",
        "reference_complexity": "O(N)",
        "key_checkpoints": [
            "전체 합 홀수면 -1",
            "두 합을 O(1) 로 갱신 (재계산 X)",
            "4*N 초과 시 -1",
        ],
        "common_pitfalls": [
            "매 step sum() 호출로 O(N^2) → TLE",
            "list pop(0) 으로 O(N^2)",
            "종료 조건 누락",
        ],
    },
    "pgs-67258": {
        "id": "pgs-67258",
        "title": "보석 쇼핑",
        "platform": "Programmers",
        "level": "Lv.3",
        "topics": ["sliding-window", "hash-map"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/67258",
        "description": "모든 종류의 보석을 포함하는 가장 짧은 연속 구간. 가변 슬라이딩 윈도우.",
        "reference_approach": "left/right 두 포인터로 윈도우 늘리며 dict 카운트 갱신, 모든 종류 포함되면 left 줄여 최소화.",
        "reference_complexity": "O(N)",
        "key_checkpoints": [
            "전체 보석 종류 수 미리 계산 (set)",
            "left 이동 시 dict 카운트 0이면 키 삭제",
            "답 [s+1, e+1] 1-index 반환",
        ],
        "common_pitfalls": [
            "left 이동을 if가 아닌 while로 좁혀야 최소 윈도우",
        ],
    },
    "pgs-42898": {
        "id": "pgs-42898",
        "title": "등굣길",
        "platform": "Programmers",
        "level": "Lv.3",
        "topics": ["dp"],
        "url": "https://school.programmers.co.kr/learn/courses/30/lessons/42898",
        "description": "M x N 격자에서 (1,1)→(M,N) 오른쪽/아래만 이동, 물웅덩이 피해 가는 경로 수 (mod 1e9+7).",
        "reference_approach": "dp[r][c] = dp[r-1][c] + dp[r][c-1]. 물웅덩이는 0. 매 갱신마다 mod.",
        "reference_complexity": "O(M * N)",
        "key_checkpoints": [
            "dp 인덱싱 (1-based vs 0-based) 일관성",
            "물웅덩이를 갱신 전에 0",
            "매 갱신마다 mod",
        ],
        "common_pitfalls": [
            "DFS 재귀로 짜면 메모이제이션 없으면 지수",
        ],
    },
}

PATTERNS: dict[str, dict] = {
    "binary-search": {
        "name_en": "Binary Search",
        "name_ko": "이분 탐색",
        "when_to_use": "정렬 배열에서 값 찾기, 또는 답이 단조성을 가지는 최적화 (parametric search).",
        "complexity": "O(log N)",
        "template": (
            "def binary_search(arr, target):\n"
            "    lo, hi = 0, len(arr) - 1\n"
            "    while lo <= hi:\n"
            "        mid = (lo + hi) // 2\n"
            "        if arr[mid] == target: return mid\n"
            "        elif arr[mid] < target: lo = mid + 1\n"
            "        else: hi = mid - 1\n"
            "    return -1"
        ),
        "common_pitfalls": [
            "lo <= hi vs lo < hi 혼동 (전자가 닫힌 구간에 안전)",
            "parametric search 단조성 증명 누락",
            "lower/upper bound 모호 → bisect 사용",
        ],
    },
    "sliding-window": {
        "name_en": "Sliding Window",
        "name_ko": "슬라이딩 윈도우",
        "when_to_use": "연속 부분배열/문자열의 통계. 가변 크기는 'longest/shortest with X' 패턴.",
        "complexity": "O(N)",
        "template": (
            "def longest_unique_substring(s):\n"
            "    seen = {}\n"
            "    left = best = 0\n"
            "    for right, c in enumerate(s):\n"
            "        if c in seen and seen[c] >= left:\n"
            "            left = seen[c] + 1\n"
            "        seen[c] = right\n"
            "        best = max(best, right - left + 1)\n"
            "    return best"
        ),
        "common_pitfalls": [
            "left 갱신 누락으로 윈도우 안 좁혀짐",
            "빠지는 원소 통계 미반영 (해시맵 누수)",
        ],
    },
    "two-pointers": {
        "name_en": "Two Pointers",
        "name_ko": "투 포인터",
        "when_to_use": "정렬 배열에서 양 끝에서 좁혀가며 쌍/구간 찾기, 또는 동방향 다른 속도.",
        "complexity": "O(N)",
        "template": (
            "def two_sum_sorted(arr, target):\n"
            "    lo, hi = 0, len(arr) - 1\n"
            "    while lo < hi:\n"
            "        s = arr[lo] + arr[hi]\n"
            "        if s == target: return (lo, hi)\n"
            "        elif s < target: lo += 1\n"
            "        else: hi -= 1\n"
            "    return None"
        ),
        "common_pitfalls": [
            "정렬 안 된 배열에 적용",
            "포인터 이동 조건 반전으로 무한 루프",
        ],
    },
    "bfs-dfs": {
        "name_en": "BFS / DFS",
        "name_ko": "너비/깊이 우선 탐색",
        "when_to_use": "그래프/격자 도달 가능, 가중치 1 최단 거리 (BFS), 연결 요소.",
        "complexity": "O(V + E)",
        "template": (
            "from collections import deque\n"
            "def bfs(graph, start):\n"
            "    visited = {start}\n"
            "    q = deque([start])\n"
            "    while q:\n"
            "        node = q.popleft()\n"
            "        for nxt in graph[node]:\n"
            "            if nxt not in visited:\n"
            "                visited.add(nxt); q.append(nxt)"
        ),
        "common_pitfalls": [
            "방문 처리를 pop 시점에 해서 중복 push",
            "DFS 재귀 한도(1000) 초과 → sys.setrecursionlimit",
        ],
    },
    "dp": {
        "name_en": "Dynamic Programming",
        "name_ko": "동적 계획법",
        "when_to_use": "최적 부분 구조 + 중복 부분 문제. 부분 답을 재사용.",
        "complexity": "보통 상태 수 × 전이 비용",
        "template": (
            "# bottom-up 격자 DP\n"
            "def grid_paths(m, n, blocked):\n"
            "    dp = [[0]*(n+1) for _ in range(m+1)]\n"
            "    dp[1][1] = 0 if (1,1) in blocked else 1\n"
            "    for r in range(1, m+1):\n"
            "        for c in range(1, n+1):\n"
            "            if (r, c) in blocked: dp[r][c] = 0; continue\n"
            "            if (r, c) != (1, 1):\n"
            "                dp[r][c] = dp[r-1][c] + dp[r][c-1]\n"
            "    return dp[m][n]"
        ),
        "common_pitfalls": [
            "top-down에서 메모이제이션 누락",
            "상태 정의 모호 (필요 변수 누락)",
            "mod 연산 누락",
        ],
    },
}


@tool
def get_algorithm_pattern(pattern_name: str) -> dict:
    """알고리즘 패턴의 설명/시간복잡도/템플릿/실수 모음을 조회한다.

    Args:
        pattern_name: 'binary-search', 'sliding-window', 'two-pointers', 'bfs-dfs', 'dp' 중 하나.
    """
    if pattern_name not in PATTERNS:
        return {"error": f"pattern '{pattern_name}' not found", "available_patterns": list(PATTERNS)}
    return PATTERNS[pattern_name]


@tool
def recommend_problems(
    topic: str | None = None,
    level: str | None = None,
    problem_id: str | None = None,
) -> list[dict]:
    """프로그래머스 문제를 토픽/레벨로 추천하거나 ID로 단건 조회한다.

    Args:
        topic: 토픽 키 ('binary-search', 'sliding-window', 'two-pointers', 'bfs-dfs', 'dp', 'hash-map', 'queue' 등).
        level: 'Lv.2', 'Lv.3' 등 레벨 부분 문자열.
        problem_id: 'pgs-<번호>' 지정 시 단건 조회 (다른 필터 무시).
    """
    def project(p):
        return {k: p[k] for k in ("id", "title", "level", "topics", "url", "description")}

    if problem_id is not None:
        return [project(PROBLEMS[problem_id])] if problem_id in PROBLEMS else []
    return [
        project(p) for p in PROBLEMS.values()
        if (not topic or topic in p["topics"])
        and (not level or level.lower() in p["level"].lower())
    ]


@tool
def review_solution(problem_id: str, user_code: str) -> dict:
    """풀이 코드 리뷰용 reference rubric을 가져온다.

    이 도구는 코드를 실행하지 않는다. 정답 접근법/복잡도/체크포인트/실수 목록을 반환하므로
    호출자(=agent)가 user_code와 rubric을 비교해 직접 리뷰를 작성한다.
    """
    if problem_id not in PROBLEMS:
        return {"error": f"problem_id '{problem_id}' not found", "available_ids": list(PROBLEMS)}
    p = PROBLEMS[problem_id]
    return {
        "problem_id": p["id"],
        "title": p["title"],
        "level": p["level"],
        "topics": p["topics"],
        "reference_approach": p["reference_approach"],
        "reference_complexity": p["reference_complexity"],
        "key_checkpoints": p["key_checkpoints"],
        "common_pitfalls": p["common_pitfalls"],
        "user_code_excerpt": user_code[:600],
    }


TOOLS = [get_algorithm_pattern, recommend_problems, review_solution]
