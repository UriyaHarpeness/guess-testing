import logging
import typing

from guess_testing import generators
from guess_testing.guess import Guesser, StopConditions

logging.basicConfig(level=logging.DEBUG)


def f(a, b):
    if len(a) == b:
        return 0
    if a[b].isdigit():
        if int(a[b]) == b:
            return 2
        return 1
    if len(a) >= 4 and a[0] == a[3]:
        return 9
    if len(a) >= 4 and a[0:2] == a[2:4]:
        return 666
    return 3


def g(a, b, c):
    if a == b == c:
        return
    if (a + b) == c:
        return
    if a * b == c:
        return
    if a ** b == c:
        return
    return


def h(a, b, c, d):
    if a / b == c:
        if a == c:
            if d:
                return 666
            return 8
        return 4
    return 0


def c():
    c()


class D:
    def jj(self, a):
        if a == 0:
            return 0
        return 1


def xx():
    pass


class A:
    @staticmethod
    def abc(v):
        return v


from enum import Enum

import pandas as pd

import ex2
from ex2 import how


class K(str, Enum):
    f = 'f'


class E:
    def __init__(self, w):
        self.w = w

    class F:
        @staticmethod
        def ff(a):
            if a == 0:
                return 0
            return 1

    class H:
        def __init__(self, x):
            self.x = x

    class G:
        @staticmethod
        def gg(a):
            if a == 0:
                return 0
            return 1

    def l(self, k=0):
        return 99

    def ll(self, k=0):
        return 99

    def k(self, a: int):
        A.abc(a)
        x = self.H(a)
        if a == 0:
            t = 9
        if a == 1:
            t = 9

        def go():
            a = 2
            b = 2
            c = 2
            d = 2
            return

        m = K('f')
        a += x.x
        self.l(k=a)
        dd = pd.DataFrame.from_dict({})
        p = 3
        ex2.wee()
        q = 0.1
        E.F.ff(self.w
               + a
               + self.w \
               )
        return xx(), A.abc(a), self.l(), E.F.ff(a) + E.G.gg(a), xx(), A.abc(a), self.l(), how(
            a), ex2.wee()


from typing import Dict, List, Set


def wot(a: bool, b: List[Dict[int, Set[str]]]):
    print(a, b)


def abc(a: typing.Union[str, int], b: typing.Union[str, int]):
    if type(a) == type(b):
        print(1)
    else:
        print(2)


def a(a: typing.Tuple[int, float, str], g: object):
    c = a / g
    return (type(a), a)


for _ in range(100):
    generators.AnyGenerator()

gg = Guesser((a,), positional=(generators.IntGenerator(0, 10), generators.ChoiceGenerator(
    [generators.IntGenerator(0, 10), generators.StringGenerator()])))
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)

gg.guess(suppress_exceptions=Exception, stop_conditions=StopConditions.CALL_LIMIT, call_limit=100)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
exit()

print(Guesser((a,)).guess(suppress_exceptions=TypeError, stop_conditions=StopConditions.EXCEPTION_RAISED).coverage)
Guesser((a,)).guess(suppress_exceptions=TypeError, stop_conditions=StopConditions.FULL_COVERAGE).print_results()
exit()

Guesser((abc,)).guess(10).print_results()
Guesser((abc,)).guess().print_results()
# exit()

e = E(666)
guesser = Guesser((wot,))
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

e = E(666)
guesser = Guesser((e.k, e.l, e.ll, A.abc, E.F.ff), (generators.IntGenerator(0, 10),), {})
guesser.guess(limit=100000, timeout=10)
guesser.print_results()
exit()

d = D()
guesser = Guesser((generators.IntGenerator(0, 10),), {}, (d.jj,))
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser((generators.StringGenerator(0, 10), generators.IntGenerator(0, 10)), {}, (f,))
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser((generators.IntGenerator(0, 10), generators.IntGenerator(0, 10), generators.IntGenerator(0, 10)), {},
                  (g,))
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser(
    (generators.IntGenerator(0, 10), generators.IntGenerator(0, 10), generators.FloatGenerator(0, 5, 0.5)),
    {'d': generators.GeneratorCollection((generators.FixedGenerator(0), generators.FixedGenerator(True)))}, (h,))
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser((), {}, (c,))
guesser.guess(timeout=10)
guesser.print_results()

x = generators.ChoiceGenerator(
    (generators.ListGenerator(2, 9, generators.IntGenerator(1, 9, 3)),
     generators.ListGenerator(2, 9, generators.ChoiceGenerator(
         (generators.TupleGenerator(2, 9, generators.IntGenerator(1, 9, 3)),
          generators.ListGenerator(2, 9, generators.IntGenerator(1, 9, 3)),
          generators.FixedGenerator('wow')))),
     generators.BoolGenerator(),
     generators.ChooseGenerator(('woo', 'hoo', 5)),
     generators.DictGenerator(0, 10, generators.StringGenerator(5, 5, generators.StringGenerator.NUMBERS),
                              generators.FloatGenerator(50, 100, 0.5)),
     generators.StringGenerator(0, 5, generators.StringGenerator.LOWERCASE)))

for _ in range(10):
    print(x())
