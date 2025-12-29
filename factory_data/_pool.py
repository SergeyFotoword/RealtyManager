import random
from typing import Callable, TypeVar

from django.db.models import Model, QuerySet

T = TypeVar("T", bound=Model)


def make_picker(
    qs_factory: Callable[[], QuerySet[T]],
    *,
    what: str,
) -> Callable[[], T]:

    cache: list[T] | None = None

    def _pick() -> T:
        nonlocal cache

        if cache is None:
            cache = list(qs_factory())
            if not cache:
                raise RuntimeError(
                    f"No {what} found. "
                    f"Run the corresponding factory first."
                )

        return random.choice(cache)

    return _pick