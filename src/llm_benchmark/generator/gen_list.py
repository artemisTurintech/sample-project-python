from random import randint
from typing import List


class GenList:
    @staticmethod
    def random_list(n: int, m: int) -> List[int]:
        """Generate a list of random integers

        Args:
            n (int): Number of integers to generate
            m (int): Maximum value of integers (exclusive)

        Returns:
            List[int]: List of random integers
        """
        result = []
        for _ in range(n):
            result.append(randint(0, m))
        return result

    @staticmethod
    def random_matrix(n: int, m: int) -> List[List[int]]:
        """Generate a matrix of random integers

        Args:
            n (int): Number of rows
            m (int): Number of columns

        Returns:
            List[List[int]]: Matrix of random integers
        """
        result = []
        for _ in range(n):
            result.append(GenList.random_list(n, m))
        return result