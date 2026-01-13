# lib.py의 Matrix 클래스를 참조하지 않음
import sys


"""
TODO:
- fast_power 구현하기 
"""


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    빠른 거듭제곱 알고리즘 구현
    분할 정복을 이용, 시간복잡도 고민!
    ㄴ 시간복잡도는 O(log exp) 같습니당...!
    """
    # 구현하세요!
    # 지수가 0, 1인 케이스 분리
    if exp == 0:
        return 1 % mod
    if exp == 1:
        return base % mod
    
    # 지수를 절반으로 나눠서 재귀적으로 계산
    half = fast_power(base, exp // 2, mod)
    
    # 지수가 홀수면 한 번 더 곱하기
    if exp % 2 == 0:
        return (half * half) % mod
    else:
        return (half * half % mod) * (base % mod) % mod

def main() -> None:
    A: int
    B: int
    C: int
    A, B, C = map(int, input().split()) # 입력 고정
    
    result: int = fast_power(A, B, C) # 출력 형식
    print(result) 

if __name__ == "__main__":
    main()
