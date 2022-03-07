from typing import Tuple, Union

from guess_testing.guess import Guesser


def i(a: Tuple[int, ...]) -> None:
    pass


def ii(a: Tuple[Union[str, int], ...]) -> None:
    pass


guesser = Guesser(i)
print(guesser.keyword['a'])
for _ in range(5):
    print(guesser.keyword['a']())

guesser = Guesser(ii)
print(guesser.keyword['a'])
for _ in range(5):
    print(guesser.keyword['a']())
