# 섬 연결하기 (Programmers Lv.3, pgs-42861)

- 플랫폼: Programmers
- 레벨: Lv.3
- 토픽: greedy, union-find
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/42861

## 문제 요약
n 개의 섬과 다리 후보들이 `costs = [[섬A, 섬B, 비용], ...]` 로 주어진다. 모든 섬을 연결하는 데 드는 **최소 비용**을 구한다. 전형적인 최소 신장 트리(MST) 문제다.

## 접근
크루스칼 알고리즘. 모든 간선을 비용 오름차순으로 정렬한 뒤, 가장 싼 간선부터 차례로 본다. 두 섬이 이미 같은 집합(연결됨)이면 추가 시 사이클이 생기므로 건너뛰고, 다른 집합이면 다리를 놓고 두 집합을 합친다(union-find). 간선을 `n-1` 개 채우면 종료한다. "지금 가장 싼 것을 고른다"는 그리디 선택이 MST 에서 최적임이 증명되어 있다.

## 복잡도
`O(E log E)`. 간선 정렬이 지배하고, union-find 연산은 거의 상수다.

## 핵심 체크포인트
- 간선을 비용 기준 오름차순 정렬한다.
- union-find 로 사이클을 검사해 같은 집합이면 건너뛴다.
- 선택한 간선이 `n-1` 개가 되면 모든 섬이 연결된 것이므로 멈춰도 된다.

## 흔한 실수
- 사이클 검사를 빼먹고 싼 간선을 무조건 더해 비용이 과다해진다.
- 프림과 크루스칼을 섞어 구현하다 우선순위 큐와 union-find 를 둘 다 어설프게 쓴다.
- union-find 에서 경로 압축을 빼 성능이 떨어진다.

## 핵심 코드
```python
def solution(n, costs):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = edges = 0
    for a, b, cost in sorted(costs, key=lambda c: c[2]):
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        parent[ra] = rb
        total += cost
        edges += 1
        if edges == n - 1:
            break
    return total
```
