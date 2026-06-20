# 너비/깊이 우선 탐색 (BFS / DFS)

## 개념
그래프나 격자를 체계적으로 순회하는 두 가지 기본 전략이다. **BFS** 는 큐를 사용해 시작점에서 가까운 노드부터 동심원처럼 퍼져 나간다. **DFS** 는 스택(또는 재귀)을 사용해 한 경로를 끝까지 파고든 뒤 되돌아온다. 둘 다 방문 집합으로 중복 방문을 막는다.

## 언제 쓰나
- 도달 가능 여부, 연결 요소 개수: BFS / DFS 모두 가능
- 가중치가 모두 1인 그래프의 최단 거리: BFS (처음 방문하는 시점이 최단)
- 모든 경로 탐색, 백트래킹, 사이클 검출: DFS
- 격자에서 영역 채우기(flood fill): BFS / DFS 모두 가능

## 시간 복잡도
정점 V, 간선 E 에 대해 `O(V + E)`. 격자에서는 칸 수에 비례한다.

## 기본 템플릿
```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in graph[node]:
            if nxt not in visited:
                visited.add(nxt)
                q.append(nxt)
    return visited
```

DFS 재귀 형태:
```python
def dfs(graph, node, visited):
    visited.add(node)
    for nxt in graph[node]:
        if nxt not in visited:
            dfs(graph, nxt, visited)
```

## 흔한 실수
- 방문 처리를 큐에서 꺼내는 시점에 해서 같은 노드를 여러 번 큐에 넣는다. push 시점에 방문 표시해야 한다.
- BFS 가 아닌 DFS 로 최단 거리를 구하려 한다. 가중치 1 최단 거리는 BFS 가 맞다.
- DFS 재귀 깊이가 1000 을 넘어 `RecursionError` 가 난다. `sys.setrecursionlimit` 또는 명시적 스택으로 전환한다.

## 연관 문제
- 타겟 넘버 (각 원소에 +/- 분기, DFS 백트래킹)
- 격자 영역 개수 세기 (flood fill)
- 미로 최단 거리 (BFS)
