from guess_testing.guess import Guesser


def b(a: int, c: int):
    if a == c:
        return 1
    if a == c - 1:
        return 1.1
    if a == c + 1:
        return 1.2
    if a == c + 2:
        return 1.3
    if a / c == 3:
        return 1.4
    if a % c == 0:
        return 1.5
    if a < c:
        return 2
    if c < a:
        return 3


gg = Guesser((b,))
gg.guess(suppress_exceptions=ZeroDivisionError)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
