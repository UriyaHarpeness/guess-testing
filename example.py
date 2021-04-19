import logging

from guess_testing import generators
from guess_testing.guess import Guesser

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


guesser = Guesser((generators.StringGenerator(0, 10), generators.IntGenerator(0, 10)), {}, f)
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser((generators.IntGenerator(0, 10), generators.IntGenerator(0, 10), generators.IntGenerator(0, 10)), {},
                  g)
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser(
    (generators.IntGenerator(0, 10), generators.IntGenerator(0, 10), generators.FloatGenerator(0, 5, 0.5)),
    {'d': generators.GeneratorCollection((generators.FixedGenerator(0), generators.FixedGenerator(True)))}, h)
guesser.guess(limit=100000, timeout=10)
guesser.print_results()

guesser = Guesser((), {}, c)
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
