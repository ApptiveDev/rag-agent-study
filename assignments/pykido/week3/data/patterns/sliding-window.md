# 슬라이딩 윈도우 (Sliding Window)

## 개념
배열이나 문자열의 **연속 구간**을 두 포인터(left, right)로 표현하고, right 를 늘려 구간을 확장하거나 left 를 늘려 구간을 축소하면서 구간 통계를 유지하는 기법이다. 매번 구간을 새로 계산하지 않고 들어오고 나가는 원소만 갱신하므로 중첩 반복을 한 번의 선형 순회로 바꾼다.

## 언제 쓰나
- "길이 K 인 연속 구간의 합/최댓값" 같은 고정 크기 윈도우
- "조건을 만족하는 가장 긴/짧은 연속 구간" 같은 가변 크기 윈도우
- 부분 문자열 문제에서 문자 빈도를 해시맵으로 추적할 때

## 시간 복잡도
left 와 right 가 각각 배열을 한 번씩만 지나가므로 전체 `O(N)`. 윈도우 내부 통계를 `O(1)` 로 갱신하는 것이 관건이다.

## 기본 템플릿
```python
def longest_unique_substring(s):
    seen = {}
    left = best = 0
    for right, c in enumerate(s):
        if c in seen and seen[c] >= left:
            left = seen[c] + 1
        seen[c] = right
        best = max(best, right - left + 1)
    return best
```

가변 윈도우 축소 형태:
```python
def shortest_subarray_at_least(nums, target):
    left = total = 0
    best = float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return best if best != float("inf") else 0
```

## 흔한 실수
- left 갱신을 빠뜨려 윈도우가 좁혀지지 않는다.
- 윈도우에서 빠지는 원소의 통계를 반영하지 않아 해시맵이 누수된다.
- 가변 윈도우에서 축소 조건을 `if` 로 써서 한 칸만 줄인다. 최소 구간을 찾으려면 `while` 로 끝까지 좁혀야 한다.
- 매 step 마다 `sum()` 을 다시 호출해 `O(N^2)` 로 만든다.

## 연관 문제
- 보석 쇼핑 (모든 종류를 포함하는 최소 구간, 가변 윈도우 + 해시맵)
- 고정 길이 부분합의 최댓값
- 중복 없는 가장 긴 부분 문자열
