from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """
        특정 위치에 MOD 연산이 적용된 값을 설정합니다
        key(tuple[int, int]): (행, 열) 인덱스
        value(int): 설정할 값
        """
        # 구현하세요!
        self.matrix[key[0]][key[1]] = value % self.MOD

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        """
        분할 정복을 이용한 행렬 거듭제곱을 수행하는 함수
        n(int): 지수
        Return:
            Matrix: 계산된 거듭제곱 행렬
        """
        # 구현하세요!
        size = self.shape[0]
        res = Matrix.eye(size)
        base = self.clone()
        for i in range(size):
            for j in range(size):
                base[i, j] = base[i, j]
        while n > 0:
            if n % 2 ==1:
                res = res @ base
            base = base @ base
            n //= 2
            
        return res

    def __repr__(self) -> str:
        """행렬의 각 행을 문자열로 변환하여 반환합니다"""
        # 구현하세요!
        return "\n".join([" ".join(map(str, row)) for row in self.matrix])