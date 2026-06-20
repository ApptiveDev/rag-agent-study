# 디스크 컨트롤러 (Programmers Lv.3, pgs-42627)

- 플랫폼: Programmers
- 레벨: Lv.3
- 토픽: heap, greedy
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/42627

## 문제 요약
각 작업이 `[요청 시각, 소요 시간]` 으로 주어진다. 한 번에 하나의 작업만 처리할 수 있고(비선점은 아님, 매 시점 재선택 가능), 각 작업의 **반환 시간(완료 시각 − 요청 시각)의 평균**을 최소화하도록 처리 순서를 정한다. 정수 부분만 반환한다. SJF(Shortest Job First) 스케줄링 문제다.

## 접근
요청 시각 기준으로 작업을 정렬해 두고, 현재 시각까지 도착한 작업들을 최소 힙(소요 시간 기준)에 넣는다. 매 처리 시점에 힙에서 **소요 시간이 가장 짧은** 작업을 꺼내 실행한다. 힙이 비어 있으면 다음 작업의 요청 시각으로 시간을 점프한다. 짧은 작업을 먼저 처리할수록 뒤에 밀리는 작업들의 대기 시간 합이 줄어든다(그리디).

## 복잡도
`O(N log N)`. 정렬과 힙 연산이 지배한다.

## 핵심 체크포인트
- 도착한(요청 시각 <= 현재 시각) 작업만 힙에 넣는다.
- 힙이 비면 일을 만들지 말고 다음 작업 요청 시각으로 시간을 이동한다.
- 반환 시간은 `완료 시각 − 요청 시각` 이고, 마지막에 작업 수로 나눠 정수화한다.

## 흔한 실수
- 단순히 요청 시각 순서대로만 처리해(FCFS) 평균을 최소화하지 못한다. 핵심은 소요 시간 기준 힙이다.
- 힙이 비었을 때 시간 점프를 빠뜨려 인덱스/시각이 어긋난다.
- 도착하지 않은 작업까지 힙에 넣어 미래 작업을 미리 실행한다.

## 핵심 코드
```python
import heapq

def solution(jobs):
    jobs.sort()
    n = len(jobs)
    time = idx = total = 0
    heap = []
    while idx < n or heap:
        while idx < n and jobs[idx][0] <= time:
            heapq.heappush(heap, (jobs[idx][1], jobs[idx][0]))
            idx += 1
        if heap:
            duration, request = heapq.heappop(heap)
            time += duration
            total += time - request
        else:
            time = jobs[idx][0]
    return total // n
```
