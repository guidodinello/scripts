import fuzzy_string_matcher as fsm

CORPUS = [
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

if __name__ == "__main__":
    # we ignore mypy error not recognizing the function inside the rust module
    similar_words = fsm.find_most_similar_words(  # type:ignore
        "yellow", CORPUS, len(CORPUS)
    )
    for word in similar_words:
        print(word.word, word.distance)
