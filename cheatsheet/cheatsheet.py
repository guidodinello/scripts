import os
import subprocess
import sys
from collections import namedtuple
from pathlib import Path
from typing import Callable, Iterable, Optional, TypeVar

from ..configreader import read_mapping_file

# Configurable Script Constants
CHEATSHEETS_FOLDER = read_mapping_file()['folder']
SIMILARITY_THRESHOLD = 4

USAGE_DOCS = f"""
Usage: cheatsheet <cheatsheet_name>

This command opens the <cheatsheet_name>.md 
located under FOLDER using in VSCode.
If no file matches <cheatsheet_name>.md, it will show an error 
and print a list of similar files.

FOLDER={CHEATSHEETS_FOLDER}
"""

word_distance = namedtuple('word_distance', ['word', 'distance'])


def find_most_similar_words(
        obj_word: str,
        word_list: Iterable[str],
        num_results: int = 10) -> Iterable[word_distance]:
    distances = [
        word_distance(
            word=word,
            distance=damerau_levenshtein_distance(obj_word, word)
        ) for word in word_list]
    distances.sort(key=lambda x: x[1])
    return distances[:num_results]


def damerau_levenshtein_distance(str1: str, str2: str) -> int:
    """ Damerau-Levenshtein distance
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
    d = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    # Initialize the first row and first column of the matrix
    for i in range(len_str1 + 1):
        d[i][0] = i
    for j in range(len_str2 + 1):
        d[0][j] = j

    # Calculate the minimum number of operations required
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            cost = 0 if str1[i-1] == str2[j-1] else 1
            d[i][j] = min(
                d[i-1][j] + 1,       # Deletion
                d[i][j-1] + 1,       # Insertion
                d[i-1][j-1] + cost   # Substitution
            )
            if i > 1 and j > 1 and \
                str1[i-1] == str2[j-2] and\
                str1[i-2] == str2[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2] + cost)  # Transposition

    return d[len_str1][len_str2]


T = TypeVar('T')


def lazy_find(p: Callable[[T], bool], iterable: Iterable[T]) -> Optional[T]:
    return next((x for x in iterable if p(x)), None)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE_DOCS)
        sys.exit(1)

    cheatsheet_name = sys.argv[1].lower()

    cheatsheet_file = lazy_find(
        lambda x: x.stem.lower() == cheatsheet_name,
        Path(CHEATSHEETS_FOLDER).glob('*.md'))

    if cheatsheet_file is None:
        print("Cheatsheet not found. Maybe you meant:")
        similar = find_most_similar_words(
            cheatsheet_name,
            [x.stem.lower() for x in Path(CHEATSHEETS_FOLDER).glob('*.md')])
        recommendations = list(
            filter(
                lambda x: x.distance < SIMILARITY_THRESHOLD,
                similar))
        if len(recommendations) == 0:
            print(f"\t* {similar[0].word}")
        else:
            for word, _ in recommendations:
                print(f"\t* {word}")

        sys.exit(1)
    else:
        subprocess.run(["code", 
            os.path.join(CHEATSHEETS_FOLDER, cheatsheet_file)], check=True)
        sys.exit(0)
