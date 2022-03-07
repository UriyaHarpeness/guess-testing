from guess_testing.guess import Guesser


def c():
    1 / 0


guesser = Guesser((c,))
guesser.guess(pretty=True)
print(guesser.coverage)
print(guesser.exceptions)
print(guesser.return_values)
