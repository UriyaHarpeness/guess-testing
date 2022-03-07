import typing

from guess_testing import generators
from guess_testing.guess import Guesser, StopConditions


def a(a: typing.Tuple[int, float, str], g: object):
    c = a / g
    return (type(a), a)


gg = Guesser((a,), positional=(generators.IntGenerator(0, 10), generators.UnionGenerator(
    [generators.IntGenerator(0, 10), generators.StringGenerator()])))

gg.guess(suppress_exceptions=Exception, stop_conditions=StopConditions.CALL_LIMIT, call_limit=100)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
