from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화
        n: 정점의 개수 (1번부터 n번까지)
        """
        self.n = n
        # 구현하세요!
        self.adj: DefaultDict[int, List[int]] = defaultdict(list)
    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가
        """
        # 구현하세요!
        self.adj[u].append(v)
        self.adj[v].append(u)
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색 (DFS)
        
        구현 방법:
        재귀 방식: 함수 내부에서 재귀 함수 정의하여 구현
        start: 탐색을 시작할 정점 번호
        Return:
            list[int]: DFS 방문 순서대로 나열된 정점 리스트
        """
        # 구현하세요!
        visited_order: list[int] = []
        visited_check: set[int] = set()

        def dfs_recursive(curr: int) -> None:
            visited_check.add(curr)
            visited_order.append(curr)
            
            #인접 리스트 정렬 후 순회
            for i in sorted(self.adj[curr]):
                if i not in visited_check:
                    dfs_recursive(i)

        dfs_recursive(start)
        return visited_order
    
    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)
        큐를 사용하여 구현
        start (int): 탐색을 시작할 정점 번호
        Return:
            list[int]: BFS 방문 순서대로 나열된 정점 리스트
        """
        # 구현하세요!
        visited_order: list[int] = []
        visited_check: set[int] = {start}
        queue: deque[int] = deque([start])

        while queue:
            curr = queue.popleft()
            visited_order.append(curr)
            
            #인접 리스트 정렬 후 순회
            for i in sorted(self.adj[curr]):
                if i not in visited_check:
                    visited_check.add(i)
                    queue.append(i)
                    
        return visited_order
    
    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))
