# Guess Testing

Welcome to Guess Testing!

Ain't nobody got the time to write unit tests! But... everybody wants a 100% coverage! If you're not a QA person (or
even if you do), this here solution is just PERFECT for you!

Test your code with Guess Testing! No more hard work searching for edge cases, possible exceptions, or immunity to weird
inputs. Save your strength and let the CPU do the hard work.

## Getting Started

First off clone this project, it is written for [Python 3.8](https://www.python.org/downloads/release/python-38/), but
due to its basic requirements can work on many other versions.

### Prerequisites

No additional packages are required for using Guess Testing, but for a pretty progress bar, `rich` is required. For the
CLI, `click` is required.

```shell script
pip install click rich
```

### Installing

You can install Guess Testing from PyPI using `pip`!

```shell script
pip install guess-testing
```

That's it!

### Usage

Guess Testing is package that can be imported and used for many reasons, such as:

1. Finding the smallest set of parameters for getting a full coverage of a scope.
2. Finding the possible exceptions the code can throw and from where, and which arguments cause these behaviors.
3. Finding all the possible return values of a function, and which arguments cause them.
4. Any form of stress testing, analysing an unknown code, and many, many more cases.
5. Supports coverage checking for instructions as well, and not only line numbers, meaning `1 if False else 0` will be
   shown as not covered.
6. Generating random values to match specific typing.
7. Generate random typing.

As a python package, it is importable, like so:

```python
import guess_testing
```

It also features a CLI, which can be used like so:

```shell script
$ guess-testing generate-from-string 'List[int]' -n 2
[49533, 8829, 6404, 14376, 1608, 29969, -22302, 55508, 13601, 61492, 10087, -2318, -33220, -56423, 46858]
[-32488, 25782]
$ gstst generate-type -n 5  
None
str
List[str]
Union[Tuple[Dict[range, Tuple[None, ...]], bool, List[Set[complex]]], Union[Iterable[complex], None, Optional[Optional[str]], Union[Dict[str, None], Union[range]], bytes, complex, float, str]]
Tuple[bool, range, Tuple[Tuple[bool, ...], ...], Tuple[Tuple[bool, ...], Set[range], str, Iterable[Set[None]], Tuple[range, ...], Union[Optional[None], int], Tuple[Tuple[bytes, ...], Union[bool, bytes, int, range], List[complex], bytes, Iterable[None], float, None, Union[bool, bytes, complex, float, int, str]]], range]
```

All the options are listed under `gstst --help`.

Guess Testing offers two main features that can be used separately, guessing and generators:

* **Guessing** - The ability to guess values for a function until specific requirements are met.
* **Generators** - The ability to generate values using explicitly constructed generators (many generators are
  available), or using the factory and retrieving a generators that correlates to the type annotation specified, or a
  function, *supports `typing` module type specifications*.

### Test Run

#### Guessing

Let's see an example of how Guess Testing can be of benefit:

```python
import typing

from guess_testing.guess import Guesser, StopConditions


def e(a: typing.List[int]) -> str:
    if len(a) == 0:
        return 'no enough'
    if len(a) == 1:
        return 'still not enough'
    if a[0] == a[1]:
        return 'wow!'
    if a[0] % a[1] == 0:
        return 'great!!'
    if a[0] % a[1] == 1:
        return 'amazing!!!'
    return 'boo...'


guesser = Guesser(e)
guesser.guess(stop_conditions=StopConditions.FULL_COVERAGE, suppress_exceptions=ZeroDivisionError, pretty=True)
print(guesser.coverage)
print(guesser.exceptions)
print(guesser.return_values)
```

Now all that's left is running the code, let's see it in action!

![Guess Testing in action](example-run.gif)

> The code in this example run can be found in [Example E](examples/example_e.py).
>
> More examples are available [here](examples).

Now how about checking a code that cannot be *really* covered (from [Example H](examples/example_h.py))?

```python
from guess_testing.guess import Guesser


def h(a: int) -> str:
    return 'a' if a == 666 else 'b'


guesser = Guesser(h, trace_opcodes=False)
guesser.guess(call_limit=10000)
print(f'Attempts: {guesser.attempts_number}, coverage: {guesser.coverage["coverage"]}.')

guesser = Guesser(h, trace_opcodes=True)
guesser.guess(call_limit=10000)
print(f'Attempts: {guesser.attempts_number}, coverage: {guesser.coverage["coverage"]}.')
```

And here is the output:

```text
Attempts: 1, coverage: 100.0.
Attempts: 10000, coverage: 77.77777777777777.
```

#### Generators

Let's review two more examples using the generators' ability (taken from [Example F](examples/example_f.py)):

```python
import typing

from guess_testing.typing_generators_factory import TypingGeneratorFactory


def e(a: typing.List[int]) -> str:
    pass


generators = TypingGeneratorFactory.get_generators(e)
print(generators)

for _ in range(10):
    print(generators['a']())
```

Now the result:

```text
{'a': List[int]}
[39784, 47413, 20590, 47366, -47725, 60081, 41957]
[35520, 54323]
[47232, -18372]
[-28274, 30664, -65376, 41264, -25118, 1267, -46631, 15847, 64907, 14002, -26615, 37780]
[]
[26879, -9958, 12824]
[-32159, -23371, -46221, 40098, 42298, 60795]
[-8062, 64305, -14024, 46788]
[-62397, 12193, -48413, -45434, -56422, -45250, 24665, 37593, -4881, -40823, 48727, 43525]
[18760, -36428, -34772, -41072, 50803, 54740, -25575, 1038, 57881, -10428, -4403, 738, -6967, -48162, 19645]
```

Here's another one, a bit more extreme ([Example G](examples/example_g.py)):

```python
from guess_testing.generators import AnyGenerator

a = AnyGenerator()
for _ in range(5):
    print(a())

for _ in range(5):
    print(a.generate_generator())
```

The output:

```text
[<generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0f005dcf0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e0008350>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00083c0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e0008510>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00089e0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e0008ac0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e0008f90>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0f00ca040>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0f00ca0b0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0f00caeb0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00fa890>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00fa900>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00fa970>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0e00fa9e0>]
[{None, 3407.2062877800927, (52160, range(210, -164, -8), None, (-42239.34660829524+31542.572884277804j), (48542.738550590744-11834.802271042106j), range(-127, -51, 4), (28303.036853390033+25426.586453325246j), False, 20651), (20846, range(140, 211, 9), None, (-9787.667116909128-36108.15226304931j), (-28326.935324770995-1654.824857357773j), range(-253, 99), (22136.88909872755+7094.531064717114j), False, -56200), 17108, 'JBygBHyd{-W8xu', 3356, -35619}, {b'#5qOb', (-20434, range(253, 178, -11), None, (-42678.645049940504-12401.42343568847j), (-31018.26686958586+9369.415989918038j), range(-69, 14, 15), (1549.5475654124602-64961.93558722615j), False, -2484), b'@9iL2Xx s@Zp[lk7M5ICsjbb,R', 37288, 'xSq6[W', (4166, range(15, -126, -11), None, (33654.207414087155+19426.691454051557j), (-38140.187482436755+62265.014593785716j), range(223, 127, -11), (-37088.19804402004+18390.61935634943j), False, 40409), 'jyg|m9Z]^&5zp&', b'S1[z_>\t]K$J;T.ZkB', "1'S", 13335.448226791937, 'S+it\\J</P', 'd1P#m&\tK7<ZF}(6k', '\tfyUX* )f\n5,fT|H2[Umm', b'W9ILoWpH#S&YJLH`+NiMEs,', (-20967, range(218, 157, -13), None, (-14123.759361549688+48866.764766850814j), (-5873.291129242614-60443.13133479848j), range(17, -88, -7), (-6320.727481127862+8443.489785797035j), False, 45913)}, set(), {b'', 'g&eB"i4F)k', 'RFZa(oS@Lg%Unke7#A>ljTk8A;vcK', 'h =t9S@d~^\t=v', b"z$'Jn #600P~ayK}>sUie\nTl7%o", 59824.09415612169, 39696, 50548.759432853345, '1[)NADERs9Kb6K*s#s6%|I$', "801v' )vyX~N2x|^=iZPsLxN3~$", 22429}, {'C2q9 *u*2_Fz;p3(2TfDitBmigD%', 49894.63728402753, 'Xh]', '.`F\\bT{Se^hA2[%1bP~17cD', -9587, b'EeTN&5VC~ 9pgxkb{/ewKZ\nY5si$z;a', 27761.176826549286, (42903, range(21, -37, -11), None, (48897.252595155674+59614.132939017785j), (44349.09291976501-10453.958254245692j), range(-29, 147, 6), (-58789.841937925914+34663.60135881053j), True, 42288), 'nb7o6W\t(JoRs8[pYjM\nfL8', 54041.97531317464, "\n'xI|d N&y997"}, {(-42538, range(175, 139, -7), None, (21153.650879510664+50674.202700177295j), (-15148.512103779402+26898.971946537786j), range(164, 238, 11), (12366.180111977039-46811.58799118672j), False, 12015), b'.^jH@MXQ{f0qOe5js)x/US2<=sXi(', 9382, '7n~rJB$W\n\nc<`GN>h+Z2E8nka5&_-!', 18.04357508927933, b'|Fs"x_G]CapGlO', b"E_.cZtfDWU}'lO{", -41195, (28699, range(251, 247, -3), None, (-16220.412941527-12576.39407433664j), (14566.187056888506-19117.171633524136j), range(87, -131, -4), (12192.628992346828-56600.26172259373j), False, -47525), 'Fs/(t7 ', '1i30E!bm2t`fx@$U%i\\|u#@)5=/aWh8'}, {15918.58817113802, (16532, range(253, 160, -11), None, (17493.227899860824-24740.113832680814j), (54029.24665775082-10901.170816058322j), range(70, 83, 10), (-56810.66409780257-18242.67334362249j), True, 42243), '76KQ0Ip', -61383, 52602, (41399, range(-114, -182, -1), None, (-12364.54894227213-60470.97724074805j), (-1585.9368784613325-54957.96565532785j), range(3, -95, -14), (-1261.6325920820673-42063.85639454314j), True, 31531), 23195, 'Kj8q%(R=.S1_8F^hFB0\\IKuCv*sb"'}]
(None, None, None, None)
{9537, -26806, -16213, -42408, -53, 42032, 25104, -64651, -47850, 24983, -42632, -56519, 19482, 18838, 52188, 23421}
-28099
Tuple[None, ...]
Tuple[Tuple[Dict[Optional[range], Union[bool, bytes]], ...], bool, complex, Tuple[Iterable[Tuple[None, ...]], ...], Tuple[Set[bytes], None, List[bool], int, range, complex, None, range], complex, List[List[bool]]]
str
int
None
```

## Technologies and Capabilities

* Guess Testing is written in [Python 3.8](https://www.python.org/downloads/release/python-38/), but due to no
  dependencies and using only builtin capabilities should work on other versions just as well.
* Does not require any additional packages.
* Features a pretty progress bar for enhanced satisfaction.
* Very lightweight.
* Flexible guessing stop conditions, like full coverage (by lines and instructions), an exception is thrown, certain
  time has passed, call count limit is reached...
* Allows getting information by coverage, return values, and exceptions.
* Easily extendable.
* Contains a string representation for the generators that fits `typing` and the builtin python types.
* Features a CLI to enable actions straight from the terminal.
* What more can I say? It's small, standalone, and can actually be of use.

## Documentation

The code is documented using [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) format.

I hope that it can answer whichever questions that may arise.

## Contributing

Feel free to contact me if you have any comments, questions, ideas, and anything else you think I should be aware of. I
would also love know to which edge cases Guess Testing helped you find, and what's the weirdest/most complicated type
you generated.

This project is licensed under the terms of the MIT license.

## Authors

* [**Uriya Harpeness**](https://github.com/UriyaHarpeness)

## Acknowledgments

* I would like to thank my wife - Tohar Harpeness, my son - Amittai Harpeness, my parents, my computer, and my free
  time, for enabling me to work on this small project, it has been fun.

* I thank [Typing](https://docs.python.org/3/library/typing.html) for their simple and versatile usage, and for being
  easily parsed.

* I thank my previous experiences trying to debug a code that isn't mine and getting to all of its cases to better
  understand it, and not being able to do so easily. Which gave me the idea for this nice package to help others like
  me.
