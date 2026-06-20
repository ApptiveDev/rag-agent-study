# 보석 쇼핑 (Programmers Lv.3, pgs-67258)

- 플랫폼: Programmers
- 레벨: Lv.3
- 토픽: sliding-window, hash-map
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/67258

## 문제 요약
진열대에 보석들이 일렬로 놓여 있고 각 칸의 보석 종류가 `gems` 로 주어진다. **모든 종류의 보석을 하나 이상 포함하는 가장 짧은 연속 구간** [start, end] 를 1-index 로 구한다. 답이 여러 개면 start 가 작은 것.

## 접근
가변 슬라이딩 윈도우 + 해시맵. right 를 늘리며 윈도우 안 보석 종류별 개수를 dict 로 센다. 윈도우가 전체 종류를 모두 포함하면, left 를 늘려 윈도우를 최대한 좁히며 최소 길이를 갱신한다. left 를 옮길 때 카운트가 0 이 된 종류는 dict 에서 삭제한다.

## 복잡도
`O(N)`. left, right 가 각각 배열을 한 번씩만 지난다.

## 핵심 체크포인트
- 전체 보석 종류 수를 미리 `set` 으로 계산해 둔다.
- left 이동 시 카운트가 0 이 되면 키를 삭제해야 "모든 종류 포함" 판정이 정확하다.
- 답은 1-index 이므로 `[left + 1, right + 1]` 로 반환한다.

## 흔한 실수
- left 축소를 `if` 로 한 칸만 줄여 최소 윈도우를 놓친다. `while` 로 끝까지 좁혀야 한다.
- 종류 개수 비교를 dict 길이 대신 잘못된 변수로 한다.
- 동일 최소 길이일 때 start 가 더 작은 답으로 갱신해버린다. 더 짧을 때만 갱신한다.

## 핵심 코드
```python
def solution(gems):
    kinds = len(set(gems))
    window = {}
    left = 0
    best = (0, len(gems) - 1)
    for right, g in enumerate(gems):
        window[g] = window.get(g, 0) + 1
        while len(window) == kinds:
            if right - left < best[1] - best[0]:
                best = (left, right)
            window[gems[left]] -= 1
            if window[gems[left]] == 0:
                del window[gems[left]]
            left += 1
    return [best[0] + 1, best[1] + 1]
```
