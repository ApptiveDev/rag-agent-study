# 다익스트라 (Dijkstra)

## 개념
음수 가중치가 없는 그래프에서 한 시작점으로부터 모든 정점까지의 최단 거리를 구하는 알고리즘이다. 아직 확정되지 않은 정점 중 거리가 가장 짧은 것을 우선순위 큐로 꺼내 확정하고, 그 정점을 거쳐 가는 경로로 인접 정점의 거리를 갱신(relaxation)한다. 한 번 확정된 정점의 거리는 다시 바뀌지 않는다.

## 언제 쓰나
- 가중치가 있는(음수 없음) 그래프의 단일 출발점 최단 경로
- 지도 길찾기, 네트워크 지연 최소화
- 가중치가 다양한 격자 이동 비용 최소화

## 시간 복잡도
우선순위 큐 구현 기준 `O((V + E) log V)`. 간선마다 최대 한 번 힙에 들어간다.

## 기본 템플릿
```python
import heapq

def dijkstra(graph, start, n):
    dist = [float("inf")] * n
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nxt, w in graph[node]:
            nd = d + w
            if nd < dist[nxt]:
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    return dist
```

## 흔한 실수
- 음수 가중치 그래프에 적용한다. 음수 간선이 있으면 벨만-포드를 써야 한다.
- 힙에서 꺼낸 거리가 이미 확정된 값보다 크면 건너뛰어야 하는데(`d > dist[node]`) 이 검사를 빠뜨려 중복 처리로 느려진다.
- 거리 배열 초기화를 0 이 아닌 무한대로 해야 하는데 0 으로 두어 갱신이 안 된다.
- 방문 배열 없이 단순 BFS 로 가중치 최단 경로를 구하려 한다.

## 연관 문제
- 가중 그래프 최단 경로
- 배달 (여러 목적지까지 최단 거리)
- 최소 비용 격자 이동
