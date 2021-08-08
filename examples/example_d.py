import typing

from example_dd import ddd
from guess_testing.guess import Guesser, StopConditions


def dd(a):
    if a % 2 == 0:
        return 2
    return 1


def d(a: typing.List[int]):
    if len(a) == 0:
        return 0
    if len(a) == 1:
        return 1
    return dd(a[0]) + ddd(a[-1])


gg = Guesser((d, dd, ddd))
gg.guess(stop_conditions=StopConditions.FULL_COVERAGE, pretty=True)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
