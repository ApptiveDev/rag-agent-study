# 해시 맵 (Hash Map)

## 개념
키를 해시 함수로 버킷에 분산시켜 평균 `O(1)` 에 삽입/조회/삭제를 지원하는 자료구조다. 파이썬의 `dict` 와 `set` 이 이에 해당한다. "이미 본 적 있는가", "몇 번 등장했는가"를 빠르게 묻는 거의 모든 문제의 기본 도구다.

## 언제 쓰나
- 등장 횟수 세기, 빈도 집계 (`collections.Counter`)
- 두 수의 합처럼 "보수가 존재하는가"를 즉시 확인할 때
- 중복 제거, 멤버십 검사
- 그룹화 (애너그램 묶기 등)

## 시간 복잡도
평균 삽입/조회 `O(1)`, 최악(해시 충돌 다발) `O(N)`. N 개 원소 처리에 전체 `O(N)`.

## 기본 템플릿
```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return (seen[target - x], i)
        seen[x] = i
    return None
```

빈도 집계:
```python
from collections import Counter

def most_common_char(s):
    counter = Counter(s)
    return counter.most_common(1)[0][0]
```

## 흔한 실수
- 리스트나 딕셔너리처럼 변경 가능한(unhashable) 객체를 키로 쓴다. 튜플로 변환해야 한다.
- 슬라이딩 윈도우와 함께 쓸 때 빠지는 원소의 카운트를 0 으로 만든 뒤 키 삭제를 빼먹어 메모리/로직이 꼬인다.
- 정렬이 필요한 결과를 dict 순회 순서에 의존한다. 삽입 순서는 보장되지만 값 기준 정렬은 별도로 해야 한다.

## 연관 문제
- 보석 쇼핑 (윈도우 내 보석 종류 카운트를 dict 로 추적)
- 두 수의 합
- 애너그램 그룹화
