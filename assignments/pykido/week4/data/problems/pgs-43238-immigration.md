# 입국심사 (Programmers Lv.3, pgs-43238)

- 플랫폼: Programmers
- 레벨: Lv.3
- 토픽: binary-search
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/43238

## 문제 요약
n 명이 입국 심사를 받아야 하고, 각 심사대의 1명당 처리 시간이 배열 `times` 로 주어진다. 모든 사람이 심사를 마치는 데 걸리는 최소 시간을 구한다. n 이 최대 10억 규모라 선형 접근은 불가능하다.

## 접근
시간 t 가 주어지면 그 안에 처리 가능한 인원은 `f(t) = sum(t // x for x in times)` 이다. t 가 커질수록 처리 인원도 단조 증가하므로, `f(t) >= n` 을 만족하는 **최소 t** 를 이분 탐색한다. 답 자체를 탐색하는 parametric search 의 전형이다.

## 복잡도
`O(M log(max(times) * n))`, M = len(times). 결정 함수 `f(t)` 가 `O(M)`, 탐색 범위가 `max(times) * n` 이다.

## 핵심 체크포인트
- 탐색 범위는 `lo = 1`, `hi = max(times) * n` 으로 충분히 크게 잡는다.
- 단조성을 명시한다: 시간이 늘면 처리 인원도 늘어난다.
- `f(mid) >= n` 이면 답 후보를 줄이는 방향(`hi = mid`)으로 lower bound 를 찾는다.

## 흔한 실수
- `lo = 0` 으로 시작하면 `0 // x == 0` 이라 무한 루프나 잘못된 경계가 생긴다.
- `hi = max(times)` 로만 두면 사람이 많을 때 답을 못 찾는다. 범위에 n 을 곱해야 한다.
- 선형 탐색은 n 이 10억 스케일이라 시간 초과(TLE).

## 핵심 코드
```python
def solution(n, times):
    lo, hi = 1, max(times) * n
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(mid // x for x in times) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo
```
