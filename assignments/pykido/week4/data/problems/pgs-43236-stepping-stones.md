# 징검다리 (Programmers Lv.4, pgs-43236)

- 플랫폼: Programmers
- 레벨: Lv.4
- 토픽: binary-search
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/43236

## 문제 요약
시작점과 도착점 사이에 바위들의 좌표 `rocks` 가 주어진다. 바위를 최대 n 개 제거할 수 있을 때, 인접한 지점 사이 거리 중 **가장 짧은 거리의 최댓값**을 구한다.

## 접근
"최소 점프 거리"가 d 이상이 되도록 만들 수 있는지를 묻는 결정 문제로 바꾼다. 목표 거리 d 가 주어지면, 정렬된 바위를 앞에서부터 보며 직전 유지 지점과의 간격이 d 미만이면 그 바위를 제거한다. 제거 횟수가 n 이하면 d 는 달성 가능하다. d 가 커질수록 제거가 더 많이 필요하므로 단조성이 성립한다. 달성 가능한 **최대 d** 를 이분 탐색한다.

## 복잡도
`O(R log(distance))`, R = len(rocks). 결정 함수가 `O(R)`, 탐색 범위가 전체 거리다.

## 핵심 체크포인트
- 바위를 정렬하고 시작점(0)과 도착점(distance)을 경계로 함께 고려한다.
- 제거 시뮬레이션은 그리디로, 마지막으로 유지한 위치만 추적한다.
- 최댓값을 찾는 upper bound 형태이므로 `feasible(mid)` 이면 `lo = mid`, 종료 시 lo 처리에 주의한다.

## 흔한 실수
- 인접 거리 배열을 정렬하는 잘못된 접근. 정렬하면 위치 정보가 사라져 단조성이 깨진다.
- d 의 탐색 범위를 좌표값이 아니라 인덱스로 잡는다.
- 시작점/도착점을 빼먹어 첫/마지막 간격을 놓친다.

## 핵심 코드
```python
def solution(distance, rocks, n):
    rocks = sorted(rocks) + [distance]

    def removable(gap):
        removed = prev = 0
        for r in rocks:
            if r - prev < gap:
                removed += 1
            else:
                prev = r
        return removed <= n

    lo, hi = 1, distance
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if removable(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
```
