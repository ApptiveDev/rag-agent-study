# 타겟 넘버 (Programmers Lv.2, pgs-43165)

- 플랫폼: Programmers
- 레벨: Lv.2
- 토픽: bfs-dfs, backtracking
- 링크: https://school.programmers.co.kr/learn/courses/30/lessons/43165

## 문제 요약
음이 아닌 정수 배열 `numbers` 의 각 원소 앞에 `+` 또는 `-` 를 붙여 순서대로 더한다. 그 결과가 `target` 이 되는 경우의 수를 구한다. DFS/백트래킹 입문에 적합한 문제다.

## 접근
각 인덱스 i 에서 현재 누적합에 `+numbers[i]` 와 `-numbers[i]` 두 갈래로 분기하는 DFS 를 돈다. 인덱스가 배열 끝(`i == len(numbers)`)에 도달하면 누적합이 target 인지 검사해 경우의 수를 센다. 상태가 `(i, sum)` 으로 정의되므로 메모이제이션 DP 로도 풀 수 있다.

## 복잡도
완전 탐색은 `O(2^N)`. `(i, sum)` 상태로 메모이제이션하면 상태 수에 비례하도록 줄일 수 있다.

## 핵심 체크포인트
- base case 를 명확히: `i == len(numbers)` 일 때 누적합 검사.
- `+` 와 `-` 두 분기를 모두 재귀 호출한다.
- 누적합은 인자로 전달해 분기마다 독립적으로 유지한다.

## 흔한 실수
- DFS 로 충분한데 BFS 로 모든 부분합을 큐에 쌓아 메모리가 폭발한다.
- 누적합을 리스트 append/pop 의 부수효과로 다뤄 분기 간 상태가 오염된다.
- base case 에서 인덱스 경계를 잘못 잡아 한 칸 더 들어가거나 덜 들어간다.

## 핵심 코드
```python
def solution(numbers, target):
    def dfs(i, total):
        if i == len(numbers):
            return 1 if total == target else 0
        return dfs(i + 1, total + numbers[i]) + dfs(i + 1, total - numbers[i])

    return dfs(0, 0)
```
