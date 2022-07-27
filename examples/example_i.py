from typing import Tuple, Union

from guess_testing.typing_generators_factory import TypingGeneratorFactory


def i(a: Tuple[int, ...]) -> None:
    pass


def ii(a: Tuple[Union[str, int], ...]) -> None:
    pass


def iii(a: Tuple[str, int]) -> None:
    pass


for func in (i, ii, iii):
    parameters_generators = TypingGeneratorFactory.get_generators(func)
    print(f'Function {func.__name__}: [a] - {parameters_generators.keyword["a"]}')
    for _ in range(5):
        print(parameters_generators.keyword['a']())
    print()
