from collections.abc import Callable, Iterable


def lazy_find[T](predicate: Callable[[T], bool], iterable: Iterable[T]) -> T | None:
    return next((x for x in iterable if predicate(x)), None)
