import typing

import click

from guess_testing.generators import AnyGenerator
from guess_testing.typing_generators_factory import TypingGeneratorFactory

TYPING_TYPES = {name: class_ for name, class_ in
                {key: getattr(typing, key) for key in dir(typing)}.items()
                if issubclass(type(class_), typing._Final)}


def validate_number(_: click.Context, param: click.Option, value: int) -> int:
    """
    Validate that the number is a positive integer.
    """
    if value < 1:
        raise ValueError(f'Value {value} is invalid for {param.opts[0]}, must be a positive integer.')
    return value


@click.command('generate-from-string', help='Generate a random value by typing string.')
@click.argument('typing_string', required=True, nargs=1, type=str)
@click.option('-n', 'number', default=1, show_default=True, callback=validate_number,
              help='Number of values to generate.')
def generate_from_string(typing_string: str, number: int):  # pylint: disable=missing-function-docstring
    generator = TypingGeneratorFactory.get_generator(eval(typing_string, TYPING_TYPES))  # pylint: disable=eval-used
    for _ in range(number):
        print(generator())


@click.command('generate-type', help='Generate a random typing type.')
@click.option('-n', 'number', default=1, show_default=True, callback=validate_number,
              help='Number of types to generate.')
def generate_type(number: int):  # pylint: disable=missing-function-docstring
    for _ in range(number):
        print(AnyGenerator.generate_generator())


@click.group(help='guess-testing CLI.')
def cli():  # pylint: disable=missing-function-docstring
    pass


cli.add_command(generate_from_string)
cli.add_command(generate_type)

if __name__ == '__main__':
    cli()
