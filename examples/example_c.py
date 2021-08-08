from guess_testing.guess import Guesser


def c():
    1 / 0


gg = Guesser((c,))
gg.guess(pretty=True)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
