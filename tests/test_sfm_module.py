"""
Tests for the sfm module's find_most_similar_words function.
"""

import pytest

from utils.sfm import sfm as fsm


def test_find_most_similar_words():
    """Test that find_most_similar_words returns expected results."""
    corpus = [
        "hello",
        "world",
        "foo",
        "bar",
        "baz",
        "qux",
        "quux",
        "corge",
        "grault",
        "garply",
        "waldo",
    ]

    # Test with a word similar to "hello"
    similar_to_hello = fsm.find_most_similar_words("helo", corpus, len(corpus))

    # Check that "hello" is the most similar word
    assert similar_to_hello[0].word == "hello"
    assert similar_to_hello[0].distance == 1

    # Test with a completely different word
    similar_to_yellow = fsm.find_most_similar_words("yellow", corpus, len(corpus))

    # Check that we get results ordered by similarity
    assert len(similar_to_yellow) > 0

    # Check that the results are sorted by distance (ascending)
    for i in range(1, len(similar_to_yellow)):
        assert similar_to_yellow[i - 1].distance <= similar_to_yellow[i].distance

    # Test with empty corpus
    empty_results = fsm.find_most_similar_words("test", [], 0)
    assert len(empty_results) == 0

    # Test with limit
    limited_results = fsm.find_most_similar_words("test", corpus, 3)
    assert len(limited_results) <= 3


def test_edge_cases():
    """Test edge cases for find_most_similar_words."""
    corpus = ["hello", "world", "test"]

    # Test with empty string
    empty_query = fsm.find_most_similar_words("", corpus, len(corpus))
    assert len(empty_query) > 0  # Should still return results

    # Test with query that matches exactly
    exact_match = fsm.find_most_similar_words("hello", corpus, len(corpus))
    assert exact_match[0].word == "hello"
    assert exact_match[0].distance == 0


if __name__ == "__main__":
    pytest.main()
