from collections.abc import Iterable
from typing import NamedTuple


class WordDistance(NamedTuple):
    """Tuple containing a word and its distance to another word"""

    word: str
    distance: int


def find_most_similar_words(
    obj_word: str,
    word_list: Iterable[str],
    num_results: int = 10,
) -> list[WordDistance]:
    """Finds the most similar words to the obj_word in the given word_list
    Args:
        obj_word (str): word to compare to
        word_list (Iterable[str]): list of words to compare with
        num_results (int, optional): number of results to retrieve.
            Defaults to 10.
    Returns:
        list[WordDistance]: list of WordDistance objects
    """
    distances = [
        WordDistance(
            word=word,
            distance=damerau_levenshtein_distance(obj_word, word),
        )
        for word in word_list
    ]
    distances.sort(key=lambda x: x[1])
    return distances[:num_results]


def damerau_levenshtein_distance(str1: str, str2: str) -> int:
    """Damerau-Levenshtein distance
    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance

    d_a,b[i,j] = min(
        d_a,b[i-1, j  ] + 1,       i>0 # Deletion
        d_a,b[i  , j-1] + 1,       j>0 # Insertion
        d_a,b[i-1, j-1] + cost,    i,j>0 # Substitution
        d_a,b[i-2, j-2] + cost,    i,j>1,
            a[i] == b[j-1], a[i-1] == b[j] # Transposition
    )
    where
        cost = 1 if a[i] != b[j] else 0
    """
    len_str1, len_str2 = len(str1), len(str2)

    # Create a matrix of size (len_str1 + 1) x (len_str2 + 1)
    distances = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    # Initialize the first row and first column of the matrix
    for i in range(len_str1 + 1):
        distances[i][0] = i
    for j in range(len_str2 + 1):
        distances[0][j] = j

    # Calculate the minimum number of operations required
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            distances[i][j] = min(
                distances[i - 1][j] + 1,  # Deletion
                distances[i][j - 1] + 1,  # Insertion
                distances[i - 1][j - 1] + cost,  # Substitution
            )
            if (
                i > 1
                and j > 1
                and str1[i - 1] == str2[j - 2]
                and str1[i - 2] == str2[j - 1]
            ):
                distances[i][j] = min(
                    distances[i][j],
                    distances[i - 2][j - 2] + cost,
                )  # Transposition

    return distances[len_str1][len_str2]
