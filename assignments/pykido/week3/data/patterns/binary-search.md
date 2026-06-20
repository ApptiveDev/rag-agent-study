# 이분 탐색 (Binary Search)

## 개념
정렬된 배열에서 탐색 범위를 절반씩 줄여가며 목표값을 찾는 기법이다. 매 단계에서 후보 구간의 중앙값을 확인하고, 목표와의 대소 관계로 한쪽 절반을 버린다. 핵심 전제는 **단조성(monotonicity)** 으로, 구간이 정렬되어 있거나 어떤 결정 함수가 한 방향으로만 변할 때만 적용할 수 있다.

## 언제 쓰나
- 정렬된 배열에서 특정 값 또는 그 삽입 위치를 찾을 때
- "조건을 만족하는 최소/최대 값"을 구하는 최적화 문제 (parametric search). 답 후보 x에 대해 `가능한가?(x)`가 단조 boolean이면 답 자체를 이분 탐색한다.
- lower bound / upper bound 가 필요할 때는 직접 구현보다 `bisect_left`, `bisect_right` 를 쓰는 것이 안전하다.

## 시간 복잡도
탐색 구간이 매 단계 절반이 되므로 `O(log N)`. parametric search 는 결정 함수 비용이 `O(f)` 일 때 `O(f log(범위))` 가 된다.

## 기본 템플릿
```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

parametric search 형태:
```python
def min_feasible(lo, hi, feasible):
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

## 흔한 실수
- `lo <= hi` 와 `lo < hi` 를 혼동한다. 닫힌 구간 인덱스 탐색은 `lo <= hi` 가 안전하다.
- parametric search 에서 단조성 증명을 건너뛴다. 단조가 아니면 이분 탐색은 오답을 낸다.
- 탐색 범위 hi 를 너무 작게 잡아 답을 놓친다. 범위는 답이 존재할 수 있는 최댓값까지 충분히 크게 잡는다.
- lower bound 와 upper bound 가 모호할 때 직접 구현하다 off-by-one 을 낸다.

## 연관 문제
- 입국심사 (parametric search, 답이 시간에 대해 단조)
- 징검다리 (최소 점프 거리를 이분 탐색)
- 정렬된 배열에서의 값 존재 여부 / 개수 세기
