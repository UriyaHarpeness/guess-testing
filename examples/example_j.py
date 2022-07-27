from guess_testing.typing_generators_factory import TypingGeneratorFactory


def j1(x: int):
    pass


def j2(x: str, /):
    pass


def j3(*, y: float):
    pass


def j4(x: int, /, y: complex):
    pass


def j5(x: int, *y: bytes, **z: bool):
    pass


for func in (j1, j2, j3, j4, j5):
    parameters_generators = TypingGeneratorFactory.get_generators(func)
    print(f'Function {func.__name__}: {parameters_generators}')
