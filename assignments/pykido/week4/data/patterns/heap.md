# 힙 / 우선순위 큐 (Heap / Priority Queue)

## 개념
삽입과 최솟값(또는 최댓값) 추출을 모두 `O(log N)` 에 처리하는 완전 이진 트리 기반 자료구조다. 파이썬 `heapq` 는 최소 힙만 제공하므로 최대 힙이 필요하면 값에 음수를 취해 넣는다. 항상 "다음으로 처리할 가장 우선순위 높은 원소"를 빠르게 꺼내야 하는 상황에서 쓴다.

## 언제 쓰나
- 매 순간 최소/최대 원소를 꺼내야 할 때 (작업 스케줄링)
- 다익스트라 최단 경로의 우선순위 큐
- 상위 K 개 원소 유지 (크기 K 힙)
- 여러 정렬된 리스트의 병합

## 시간 복잡도
삽입/추출 각각 `O(log N)`, 최소값 확인은 `O(1)`. 리스트로부터 힙 생성(`heapify`)은 `O(N)`.

## 기본 템플릿
```python
import heapq

def k_smallest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
    return [heapq.heappop(heap) for _ in range(k)]
```

작업 스케줄링 골격:
```python
import heapq

def schedule(jobs):
    jobs.sort()
    heap = []
    time = idx = total = 0
    while idx < len(jobs) or heap:
        while idx < len(jobs) and jobs[idx][0] <= time:
            heapq.heappush(heap, jobs[idx][1])
            idx += 1
        if heap:
            duration = heapq.heappop(heap)
            time += duration
            total += time  # 단순화한 형태
        else:
            time = jobs[idx][0]
    return total
```

## 흔한 실수
- 최대 힙을 직접 구현하려다 실수한다. 음수 부호 트릭이 간단하다.
- 힙의 임의 위치 원소를 직접 수정하면 힙 불변식이 깨진다. 갱신이 필요하면 lazy deletion 을 쓴다.
- 튜플을 넣을 때 첫 원소가 동률이면 두 번째 원소로 비교가 넘어간다. 비교 불가능한 객체를 두 번째에 두면 오류가 난다.

## 연관 문제
- 디스크 컨트롤러 (요청을 도착 시간순으로 보며 작업 시간이 짧은 것을 힙에서 우선 처리)
- 다익스트라
- 상위 K 빈도 원소
