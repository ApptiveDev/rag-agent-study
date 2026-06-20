# 누적 합 (Prefix Sum)

## 개념
배열의 앞에서부터 누적한 합을 미리 계산해 두면, 임의 구간 `[i, j]` 의 합을 `prefix[j+1] - prefix[i]` 로 `O(1)` 에 구할 수 있다. 구간 합을 여러 번 질의해야 하는 상황에서 매번 다시 더하는 `O(N)` 작업을 `O(1)` 로 줄인다. 2차원으로 확장하면 부분 직사각형 합도 `O(1)` 에 얻는다.

## 언제 쓰나
- 구간 합을 여러 번 질의할 때
- "합이 K 인 부분 배열의 개수" (누적 합 + 해시맵)
- 2차원 격자에서 부분 직사각형 합

## 시간 복잡도
누적 합 전처리 `O(N)`, 이후 각 구간 질의 `O(1)`. 2차원은 전처리 `O(M*N)`, 질의 `O(1)`.

## 기본 템플릿
```python
def build_prefix(nums):
    prefix = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    return prefix

def range_sum(prefix, i, j):
    return prefix[j + 1] - prefix[i]
```

합이 K 인 부분 배열 개수:
```python
from collections import defaultdict

def subarray_sum_k(nums, k):
    count = total = 0
    seen = defaultdict(int)
    seen[0] = 1
    for x in nums:
        total += x
        count += seen[total - k]
        seen[total] += 1
    return count
```

## 흔한 실수
- prefix 배열 크기를 N 으로 잡아 경계 인덱스에서 틀린다. 보통 `N+1` 로 두고 prefix[0]=0 으로 시작하면 깔끔하다.
- 구간 합 공식에서 `prefix[j] - prefix[i]` 처럼 off-by-one 을 낸다.
- 음수가 섞인 배열에서 "합이 K" 문제를 슬라이딩 윈도우로 풀려 한다. 음수가 있으면 누적 합 + 해시맵이 맞다.

## 연관 문제
- 합이 K 인 부분 배열의 개수
- 구간 합 질의
- 2차원 부분 행렬 합
