# 등굣길 (Programmers Lv.3, pgs-42898)

- 플랫폼: Programmers
- 레벨: Lv.3
- 토픽: dp
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/42898

## 문제 요약
m x n 격자에서 (1,1) 에서 출발해 (m,n) 까지 **오른쪽 또는 아래로만** 이동한다. 물에 잠긴 칸 `puddles` 는 지날 수 없다. 가능한 경로의 수를 `1,000,000,007` 로 나눈 나머지로 구한다.

## 접근
격자 DP. `dp[r][c]` 를 (1,1) 에서 (r,c) 까지의 경로 수로 정의한다. 각 칸으로 오는 방법은 위에서 내려오거나 왼쪽에서 오는 두 가지뿐이므로 `dp[r][c] = dp[r-1][c] + dp[r][c-1]`. 물웅덩이는 0 으로 고정한다.

## 복잡도
모든 칸을 한 번씩 채우므로 `O(m * n)`.

## 핵심 체크포인트
- 인덱싱을 1-based 로 통일하면 경계 처리가 간단하다 (`dp` 크기를 `(m+1) x (n+1)`).
- 물웅덩이를 갱신하기 전에 0 으로 막는다.
- 매 갱신마다 `% 1_000_000_007` 을 적용한다.

## 흔한 실수
- DFS 재귀로 풀면서 메모이제이션을 안 해 경로 수가 지수적으로 폭발한다.
- 모듈러 연산을 마지막에 한 번만 해서 중간 오버플로(다른 언어)나 누적 오류가 난다.
- 시작 칸 `dp[1][1]` 초기화를 빠뜨린다.

## 핵심 코드
```python
def solution(m, n, puddles):
    MOD = 1_000_000_007
    blocked = {(c, r) for c, r in puddles}
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    dp[1][1] = 1
    for r in range(1, n + 1):
        for c in range(1, m + 1):
            if (c, r) == (1, 1):
                continue
            if (c, r) in blocked:
                dp[r][c] = 0
                continue
            dp[r][c] = (dp[r - 1][c] + dp[r][c - 1]) % MOD
    return dp[n][m]
```
