import typing

from guess_testing.generators import TypingGeneratorFactory


def e(a: typing.List[int]) -> str:
    pass


generators = TypingGeneratorFactory.get_generators(e)
print(generators)

for _ in range(10):
    print(generators['a']())
