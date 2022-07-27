import typing

from guess_testing.typing_generators_factory import TypingGeneratorFactory


def f(a: typing.List[int]) -> str:
    pass


generators = TypingGeneratorFactory.get_generators(f)
print(generators)

for _ in range(10):
    print(generators.keyword['a']())
