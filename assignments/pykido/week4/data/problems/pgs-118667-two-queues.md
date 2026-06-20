# 두 큐 합 같게 만들기 (Programmers Lv.2, pgs-118667)

- 플랫폼: Programmers
- 레벨: Lv.2
- 토픽: two-pointers, queue
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/118667

## 문제 요약
길이가 같은 두 큐 `queue1`, `queue2` 가 주어진다. 한쪽에서 원소를 빼 다른 쪽에 넣는 작업을 반복해 두 큐의 합을 같게 만드는 **최소 작업 횟수**를 구한다. 불가능하면 -1.

## 접근
두 큐를 덱으로 두고, 한 큐의 합이 더 크면 그 큐의 앞 원소를 빼서 다른 큐의 뒤에 넣으며 두 합을 맞춰 간다(투 포인터처럼 한 방향으로만 옮긴다). 합이 같아지면 종료한다. 전체 합이 홀수면 절대 같아질 수 없으므로 -1. 합 갱신을 `O(1)` 로 하는 것이 핵심이다.

## 복잡도
`O(N)`. 작업 횟수 상한이 `4 * N` 이내라 그 안에 못 맞추면 -1 로 판정한다.

## 핵심 체크포인트
- 전체 합이 홀수면 즉시 -1.
- 두 큐의 합을 매번 재계산하지 말고, 옮기는 원소만큼 `O(1)` 로 갱신한다.
- 작업 횟수가 `4 * N` 을 넘으면 -1.

## 흔한 실수
- 매 스텝마다 `sum()` 을 호출해 `O(N^2)` 로 만들어 TLE.
- `list.pop(0)` 으로 앞에서 빼서 `O(N)` 비용 → 전체 `O(N^2)`. `collections.deque` 를 쓴다.
- 종료 상한 조건을 빼먹어 같아지지 않는 입력에서 무한 루프.

## 핵심 코드
```python
from collections import deque

def solution(queue1, queue2):
    q1, q2 = deque(queue1), deque(queue2)
    s1, s2 = sum(q1), sum(q2)
    if (s1 + s2) % 2:
        return -1

    for count in range(4 * len(queue1)):
        if s1 == s2:
            return count
        if s1 > s2:
            x = q1.popleft()
            s1 -= x
            s2 += x
            q2.append(x)
        else:
            x = q2.popleft()
            s2 -= x
            s1 += x
            q1.append(x)
    return -1
```
