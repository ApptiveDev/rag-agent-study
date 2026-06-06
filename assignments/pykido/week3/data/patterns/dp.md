# 동적 계획법 (Dynamic Programming)

## 개념
큰 문제를 겹치는 작은 부분 문제로 나누고, 부분 문제의 답을 저장해 재사용하는 기법이다. 두 가지 전제가 모두 성립해야 한다. **최적 부분 구조** (큰 문제의 최적해가 부분 문제의 최적해로 구성됨) 와 **중복 부분 문제** (같은 부분 문제가 여러 번 등장함). 구현은 재귀 + 메모이제이션의 top-down 과 반복문의 bottom-up 두 가지가 있다.

## 언제 쓰나
- 경우의 수 세기 (경로 수, 조합 수)
- 최소 비용 / 최대 가치 최적화 (배낭, 동전 교환)
- 부분 수열 문제 (최장 증가 부분 수열, 편집 거리)

## 시간 복잡도
일반적으로 `상태 개수 × 상태당 전이 비용`. 격자 DP 는 보통 `O(M*N)`, 배낭은 `O(N*W)` 이다.

## 기본 템플릿
bottom-up 격자 DP:
```python
def grid_paths(m, n, blocked):
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    dp[1][1] = 0 if (1, 1) in blocked else 1
    for r in range(1, m + 1):
        for c in range(1, n + 1):
            if (r, c) in blocked:
                dp[r][c] = 0
                continue
            if (r, c) != (1, 1):
                dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[m][n]
```

top-down 메모이제이션:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

## 흔한 실수
- 상태 정의가 모호해 필요한 변수가 누락된다. "dp[i] 가 무엇을 의미하는가"를 한 문장으로 적을 수 있어야 한다.
- top-down 에서 메모이제이션을 빠뜨려 지수 시간으로 퇴화한다.
- 경우의 수 문제에서 모듈러 연산을 매 갱신마다 적용하지 않아 오버플로 또는 오답이 난다.
- 1-based 와 0-based 인덱싱을 섞어 경계에서 틀린다.

## 연관 문제
- 등굣길 (격자 경로 수, 물웅덩이 회피, mod 1e9+7)
- 최장 증가 부분 수열
- 0/1 배낭
