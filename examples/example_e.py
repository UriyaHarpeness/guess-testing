import typing

from guess_testing.guess import Guesser, StopConditions


def e(a: typing.List[int]) -> str:
    if len(a) == 0:
        return 'no enough'
    if len(a) == 1:
        return 'still not enough'
    if a[0] == a[1]:
        return 'wow!'
    if a[0] % a[1] == 0:
        return 'great!!'
    if a[0] % a[1] == 1:
        return 'amazing!!!'
    return 'boo...'


gg = Guesser(e)
gg.guess(stop_conditions=StopConditions.FULL_COVERAGE, suppress_exceptions=ZeroDivisionError, pretty=True)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
