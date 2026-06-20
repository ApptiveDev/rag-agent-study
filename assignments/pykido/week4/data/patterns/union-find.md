# 유니온 파인드 (Union-Find / Disjoint Set)

## 개념
원소들을 서로소 집합으로 관리하며 "두 원소가 같은 집합에 속하는가"(find)와 "두 집합을 합치기"(union)를 거의 상수 시간에 처리하는 자료구조다. 각 원소가 자기 집합의 대표(루트)를 가리키는 트리로 표현하고, **경로 압축**과 **랭크/크기 기반 합치기** 두 최적화를 함께 적용한다.

## 언제 쓰나
- 그래프의 연결 요소 개수 세기
- 사이클 존재 여부 판정
- 크루스칼 최소 신장 트리에서 간선 추가 시 사이클 검사

## 시간 복잡도
경로 압축 + union by rank 를 적용하면 연산당 거의 상수, 정확히는 역 애커만 함수 `O(α(N))`. 사실상 `O(1)` 로 봐도 된다.

## 기본 템플릿
```python
class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
```

## 흔한 실수
- 경로 압축을 빼먹어 트리가 한쪽으로 길어지고 find 가 느려진다.
- union 전에 양쪽의 루트를 비교하지 않고 `parent[a]=b` 처럼 직접 연결해 잘못된 집합을 만든다.
- 사이클 검사에서 이미 같은 루트인 경우(union 이 False) 처리를 빠뜨린다.

## 연관 문제
- 섬 연결하기 (크루스칼에서 사이클 방지용으로 union-find 사용)
- 친구 관계 그룹 수
- 그래프 연결성 판정
