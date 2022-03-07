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

No additional packages are required for using Guess Testing, but for a pretty progress bar, `rich` is required.

```shell script
pip install rich
```

### Installing

You can install Guess Testing using PyPI!

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

As a python package, it is importable, like so:

```python
import guess_testing
```

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


gg = Guesser(e)
gg.guess(stop_conditions=StopConditions.FULL_COVERAGE, suppress_exceptions=ZeroDivisionError, pretty=True)
print(gg.coverage)
print(gg.exceptions)
print(gg.return_values)
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


gg = Guesser(h, trace_opcodes=False)
gg.guess(call_limit=10000)
print(f'Attempts: {gg.attempts_number}, coverage: {gg.coverage["coverage"]}.')

gg = Guesser(h, trace_opcodes=True)
gg.guess(call_limit=10000)
print(f'Attempts: {gg.attempts_number}, coverage: {gg.coverage["coverage"]}.')
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

from guess_testing.generators import TypingGeneratorFactory


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

for _ in range(5):
    a = AnyGenerator()
    print(a)
    print(a())
```

The output:

```text
Any[Tuple[List[Iterable[Tuple[bytes, float, int, bytes, float, range, str]]]]]
([<generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b015cf20>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b015cf90>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182040>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b01820b0>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182120>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182190>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182200>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182270>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa080047890>, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa080047900>],)
Any[Tuple[Set[range], Union[Set[str], Union[Iterable[range], Set[range], List[float], Optional[bytes], int, Tuple[str, str, bytes, int], float], bytes, Tuple[List[float], Tuple[str]], range, str, Optional[range], float, str], bytes, float, bytes]]
({range(238, 244, 2)}, {'pW"}LaH yjsVAS', 'NM%{1#r"^L2q8h73  ', 'fOpfu}a<b,6vH^bn#I%Y;j5i}.d9M', '5P<)m8LMu', '#>rc2+FWu<5[")8'}, b'a{B\n[u/k', -24513.23719166976, b'\t3JB6EX~=0KEx@;M@d|')
Any[str]
]mLQ@"#0; O&()9}kaQ1wN	
Any[Tuple[List[Tuple[range, int, range, range, Union[bytes, str, range, bytes, str, int, bytes, float, int], range, List[float]]], bytes, bytes, float, int, Iterable[Set[int]], Set[float]]]
([(range(162, 29, -1), -33964, range(-17, -236, -10), range(-182, -145, 13), range(119, 235, 12), range(212, 208, -1), [12384.572003987865, -47640.00671228561, -57324.16053851241, 3733.0225044850085, 47801.15323751047, -6421.032160359799, 26428.81500890413]), (range(57, -191, -6), 64735, range(101, -35, -8), range(8, 161, 4), b'2+pX4DC9exa', range(33, 188, 5), [16190.336032097883, 50355.5108072967, 59386.143817150034, -13012.341449025902, -21461.614964114196, 54358.986495859834, 6593.60178536865, -27373.0839303807, -16225.701842274357, -62158.48002528354, 16239.16684882225, -35754.96494490212]), (range(234, 242, 8), -21730, range(-169, -23, 14), range(71, 185, 9), b'uJ>C7c_', range(-135, 40, 10), [-4427.185045163089, 43503.63750767613, 36476.15873974668, -59683.7765906789, 36320.584551655455, -18570.628734820653, -49266.67261182533, -50716.32641721262, -3037.2482725261216, 8417.79227333964, -9395.358018240571, 6077.410199977327, -53700.12900000933])], b'M/\nis-}D.', b']S', 41242.89996328451, -9934, <generator object IterableGenerator.__call__.<locals>.<genexpr> at 0x7fa0b0182040>, {64010.095590029945, 9293.955606657793, 32176.58458371942, 29173.818421146294, -9608.87372275874, -57798.13792524391, 48510.602790748366})
Any[List[Set[Tuple[range]]]]
[set(), {(range(90, 26, -12),), (range(-44, 130, 3), range(-95, -144, -1)), ()}, {(range(2, 97, 14), range(178, 37, -10), range(-132, 20, 13), range(2, -30, -6), range(183, 200, 14), range(201, 205, 2), range(30, 154, 3), range(-35, -180, -11), range(230, 220, -3), range(181, -63, -15), range(113, -180, -12), range(-54, -155, -8), range(211, 235, 3)), (range(-85, 158, 13), range(141, 170, 6), range(246, 175, -11), range(222, 12, -3), range(167, 242, 10), range(208, 219, 5), range(167, 67, -12), range(-241, -15, 12), range(215, -33, -3), range(2, 205, 5), range(227, -74, -11), range(-72, -33, 3), range(193, -100, -6)), (range(99, -16, -2), range(255, 256), range(-86, 229, 9), range(159, -49, -6), range(246, 35, -13), range(251, 254, 2), range(150, 82, -5), range(256, 248, -4), range(49, 97, 7), range(215, -4, -11), range(246, 255, 4), range(34, 59, 9)), (range(143, 108, -15), range(232, 152, -1), range(219, 180, -4), range(255, 88, -5)), (range(249, 214, -11), range(97, -46, -3), range(187, 190), range(156, 195, 10), range(229, 180, -15), range(199, 66, -14)), (range(-36, 137, 8), range(186, -43, -8), range(236, 239), range(222, 62, -12), range(-155, 254, 10), range(-161, 91, 6)), (range(93, -43, -14), range(-10, 95, 10), range(253, -18, -9), range(168, 219, 2), range(233, -158, -11), range(94, 195, 12), range(100, 207, 9), range(213, -199, -5), range(210, 199, -10), range(-26, 235, 12), range(-76, 180, 15), range(252, 238, -7), range(59, 187, 6), range(-207, -218, -6), range(56, -96, -13)), (range(-4, 30, 8), range(-56, -10, 12), range(198, 87, -16), range(46, 103, 12), range(101, -39, -12), range(209, 36, -13), range(247, -75, -6)), (range(255, 251, -4),), (range(193, -134, -10), range(171, 203, 12), range(-3, 22)), (range(77, -215, -3), range(75, 170, 14)), (), (range(-139, 150, 13), range(252, 235, -5), range(-143, -206, -7), range(231, 241, 8), range(-166, 230, 10), range(-190, 170, 5), range(245, 44, -13), range(-84, 138, 13), range(-249, -155, 3), range(231, -82, -3), range(85, 38, -15), range(-148, 189, 6), range(232, 227, -3)), (range(-13, -206, -2), range(135, 177, 12), range(253, 254), range(-14, 112, 12), range(238, 136, -4))}, {(range(-224, 238, 10), range(-49, 152, 15), range(-212, -238, -1), range(-15, 196, 15), range(-89, 19, 10), range(250, 197, -7), range(153, -26, -3), range(-106, 114, 4), range(102, -45, -7), range(-68, -105, -11)), (range(73, 232, 5), range(252, 243, -7), range(-235, -191, 9)), (range(105, -58, -16), range(-37, 130, 8), range(-66, 233, 8), range(-82, 126), range(-106, 195, 5), range(128, 183, 15), range(-18, 170, 13), range(182, 173, -8), range(66, -127, -5), range(-106, -127, -5), range(231, 243, 8), range(-211, 22, 12), range(156, 236, 14), range(254, 74, -4), range(255, 217, -12)), (range(40, 115), range(-4, 0, 4), range(132, -183, -2), range(-46, -83, -2), range(-212, 0, 12), range(-10, -238, -2), range(233, 247, 14), range(-193, -214, -14), range(193, 190, -3), range(234, -13, -15), range(147, 78, -7), range(51, 105)), (range(-4, 173, 8), range(-209, 49, 8), range(-4, 14, 9), range(40, 167), range(-32, -9, 8), range(149, 88, -15), range(237, 197, -12), range(99, 65, -2), range(145, 90, -9), range(-96, 134, 12), range(57, -3, -13), range(217, -86, -9), range(121, 175, 14), range(255, 254, -1), range(-74, 14, 7), range(230, 183, -10)), (range(200, 251, 6), range(216, 206, -9), range(-156, 118, 5), range(124, 73, -2), range(215, 76, -7), range(-166, 186, 5), range(251, 244, -6), range(34, 190, 15), range(-193, 8, 2), range(104, 136, 10), range(235, 233, -2), range(233, 159, -10), range(184, 10, -15), range(79, -10, -13), range(153, -249, -15)), (range(237, 128, -15), range(219, 90, -5), range(116, -228, -8), range(255, 256), range(193, 132, -2), range(15, 26, 6), range(-35, -204, -3), range(154, 84, -16), range(58, -37, -4), range(221, 174, -10), range(239, 156, -15), range(-93, -60, 8), range(-236, -246, -6), range(-43, -149, -8), range(-24, -41, -14), range(229, 247, 11))}, {(range(-85, 224, 3), range(-234, 1, 5), range(5, -126, -1), range(3, 243, 14), range(-141, 161, 2), range(83, -175, -10), range(29, -197, -11), range(70, 140, 2), range(125, 209, 15), range(44, -225, -2), range(209, 34, -10), range(221, -119, -10), range(198, 74, -9)), (range(-32, 141, 15), range(188, 29, -3), range(-102, -68, 9), range(239, 246, 7), range(-170, 120, 2), range(166, -235, -9), range(35, 132, 6), range(-174, -63, 14), range(29, -7, -12), range(-24, 69, 9), range(151, 174, 13), range(81, -11, -5), range(115, 232, 9)), (range(75, 133, 9), range(-130, -255, -11), range(181, 77, -7), range(-129, -25, 13), range(193, 238, 3), range(246, 204, -9), range(146, 243, 8), range(50, 5, -6)), (range(205, -81, -13),), (range(250, 248, -2), range(70, -20, -11), range(231, 189, -14), range(-154, 63, 6), range(-40, -193, -13), range(-242, 199, 14)), (range(191, 240, 15), range(29, 145, 6), range(254, 140, -4), range(52, 234, 4), range(-51, -85, -14), range(137, 125, -5), range(30, -148, -3), range(-183, -138, 8), range(25, -11, -2)), (range(208, -232, -8), range(-108, -54, 4), range(-255, -165, 10), range(-17, 256, 5), range(180, 144, -12), range(48, 193, 6), range(5, -82, -2), range(-88, -60, 4), range(-239, -209, 11), range(-27, 129, 4)), (range(-205, -224, -11), range(200, 203, 2), range(-102, 244, 2), range(-191, -95, 14), range(55, -253, -1), range(-51, 242, 13)), (range(45, -1, -7), range(-55, 104, 11), range(-129, 34, 6), range(-79, 47, 6), range(118, -204, -8)), (range(-188, 43, 11), range(255, -51, -4), range(163, 67, -7), range(182, 108, -11), range(-60, -23, 6), range(-235, -86, 6), range(243, 102, -11), range(212, 88, -1), range(0, 19, 7), range(-74, -113, -9)), (range(-58, 226, 5), range(-227, 140, 14), range(171, 159, -9), range(222, 127, -7), range(249, 189, -12), range(-35, 13, 4), range(235, 203, -2), range(232, -113, -8), range(-20, 159, 11)), (range(77, 142, 3), range(109, -62, -2)), (range(163, -219, -8), range(27, -205, -14), range(148, -117, -2), range(-56, -150, -13), range(36, 118, 15), range(136, -13, -13), range(102, 105, 2), range(-112, -114, -2), range(167, -248, -2), range(123, -59, -7)), (range(91, 127, 3), range(16, 73), range(51, -88, -9), range(83, 42, -7), range(-102, -190, -11)), (range(-117, 168, 2), range(-175, -195, -8), range(-144, 68, 7), range(173, 242, 15), range(212, 216), range(237, 225, -6), range(142, -174, -11))}, {(range(122, 23, -3), range(42, 10, -7), range(153, 61, -13), range(150, -144, -1), range(-146, -137, 9), range(-221, 235, 8), range(-198, -136, 15), range(12, 53, 11), range(-123, 32, 3), range(239, 243), range(249, 188, -7)), (range(254, 211, -7), range(225, 221, -1)), (range(255, 253, -2), range(153, 194, 8), range(-231, -16, 14), range(-65, 182, 5), range(-25, -79, -7), range(29, 228, 13), range(-150, 1, 5)), (range(162, -11, -6), range(-147, 234, 5), range(-213, -89, 13), range(34, -245, -10), range(254, 245, -7), range(210, -47, -15)), (range(227, 249, 14), range(-195, -148, 2), range(-57, 111, 15), range(-22, 130, 8), range(189, 156, -3), range(-48, -80, -12), range(113, 211, 4)), (range(111, 42, -13), range(195, 71, -12), range(12, -193, -7)), (range(134, 148, 3), range(239, 182, -10), range(217, -47, -9), range(247, 250, 2), range(111, 54, -9), range(-72, 156, 8), range(-47, -86, -7), range(185, 210, 15), range(-48, 103, 8), range(-131, 162, 8), range(130, 101, -10), range(-44, 48, 12), range(166, 191, 6), range(24, 37, 12), range(37, 201, 11), range(-58, -78, -5)), (range(52, -100, -12), range(160, 121, -15), range(74, 44, -8), range(-81, 177, 8)), (range(-20, -53, -5), range(132, 110, -6), range(-74, -127, -6), range(109, -131, -3)), (range(17, 61, 2), range(165, -236, -2), range(83, 61, -15), range(214, 209, -1), range(72, -239, -13), range(222, -79, -6)), (range(183, 186, 2), range(234, 253, 11), range(-231, -41, 4), range(152, 227, 2), range(160, 208, 14)), (range(193, 239, 15), range(46, 250, 15), range(-246, 230, 5), range(250, -241, -7), range(72, 178, 5), range(117, 244, 13), range(232, -46, -16)), (range(202, 61, -15), range(195, 203, 2), range(-96, -58, 6), range(134, 196, 10), range(255, 95, -4), range(-172, 100, 12), range(-109, 256, 14), range(46, 252, 14)), (range(239, -130, -6), range(152, 53, -3), range(143, 37, -13), range(134, 120, -14), range(-148, -189, -15), range(131, 63, -14), range(-178, -231, -7), range(196, -125, -3), range(4, 15, 11), range(42, 148, 3), range(82, 156, 11), range(206, 145, -15), range(186, -136, -1)), (range(93, 166, 5), range(189, 221, 2), range(224, -28, -2), range(232, -40, -6))}, {(range(180, 94, -13), range(211, -140, -10), range(200, 218, 11), range(190, 236, 12)), (range(195, 159, -16), range(-167, 10, 15), range(114, 251, 10), range(170, -247, -10), range(-97, -170, -7))}, {(range(209, 112, -3), range(-30, 169), range(-97, -104, -7), range(209, -105, -3), range(89, 22, -10), range(-115, -43, 7), range(84, -150, -14), range(34, -6, -3), range(111, 181, 15), range(-173, -69), range(96, 103, 5), range(-23, -109, -13)), (range(229, 224, -2), range(-186, 224, 4), range(250, 256, 4), range(138, -16, -2), range(-44, 220, 5), range(-13, 25, 9), range(-59, -49, 7), range(49, 2, -14)), (range(185, 224, 6), range(91, -196, -2), range(-9, -188, -16), range(7, -39, -3), range(-41, 75, 13), range(156, 44, -1), range(229, 143, -14), range(42, -99, -9), range(256, 242, -8), range(230, 229, -1), range(22, 14, -5), range(131, 165, 9)), (range(208, -183, -3), range(-249, -68, 11), range(225, 59, -1), range(-136, 157, 5), range(119, 26, -4), range(90, 181, 2)), (range(37, 186, 10), range(-84, 74, 6)), (range(54, 52, -1), range(218, 219), range(111, -124, -12), range(32, -81, -14), range(9, -22, -5), range(-216, -15, 9), range(11, 156, 13), range(217, 251, 12), range(25, 201, 14), range(-251, -112, 14)), (range(229, 206, -13), range(145, 88, -11))}, {(range(-132, 131, 8), range(219, 49, -13), range(-1, 176, 8), range(215, 202, -1), range(-28, 155, 2), range(248, 238, -6), range(210, -62, -1), range(-101, -57, 9), range(-5, -69, -1), range(105, 223, 9), range(-20, 42, 5), range(235, 225, -3), range(98, 138, 10), range(157, 153, -4), range(74, 5, -4)), (range(207, -18, -3), range(-248, -212, 9)), (range(201, 119, -1), range(203, -176, -3)), (range(116, 13, -14), range(225, 154, -2), range(175, -143, -15), range(-202, 202, 10), range(240, 236, -3), range(128, 114, -4), range(58, -13, -5), range(-70, -130, -13), range(-66, 21, 12), range(14, 163, 9), range(-81, -54, 10), range(-193, -2, 7), range(40, -23, -8), range(-63, 79, 7), range(-27, -140, -10), range(246, -68, -2)), (range(143, 177, 8), range(217, 244), range(191, 243, 2), range(-134, -121, 3), range(180, 92, -16), range(75, 208, 4), range(169, -187, -3), range(145, 252, 6), range(191, 223, 7), range(-52, 37, 14), range(-77, 131, 11), range(-239, 149, 2), range(221, 90, -2), range(241, 237, -2)), (range(118, 203, 6), range(-188, 117, 9), range(174, -77, -10), range(-196, -160, 15), range(243, 210, -2), range(119, -111, -9), range(232, -37, -2)), (range(228, 203, -11), range(125, 157, 5), range(-7, 109), range(73, 27, -5), range(209, 73, -2), range(3, -251, -1), range(-147, -126, 13), range(-38, -116, -6), range(242, 129, -15), range(-24, 238), range(138, 40, -2), range(-2, 75, 14), range(72, 61, -4)), (range(51, 47, -2), range(-125, -49, 4), range(237, 179, -3), range(46, -251, -7), range(220, 189, -3), range(14, 208, 12), range(-216, 237, 12), range(-200, 72, 11), range(-48, 25, 8), range(216, 193, -14), range(167, 12, -6), range(-33, 54, 7), range(80, 189, 12), range(-207, -22, 5)), (range(184, 214, 5), range(-160, 144, 13), range(118, 37, -5), range(-236, -226, 7), range(137, 89, -8), range(253, 254), range(160, 173, 12), range(203, 181, -5), range(190, 89, -2), range(159, 223, 15), range(256, 243, -11)), (range(25, -27, -4), range(183, -3, -12), range(69, -148, -8), range(102, 221, 12), range(132, 157, 4), range(-98, -160, -2), range(80, 175), range(238, 237, -1), range(-186, -221, -6), range(-199, 159, 6)), (range(-251, -244, 5), range(197, -28, -14), range(135, 240, 15), range(164, -228, -4), range(46, 79, 7), range(51, 198, 13), range(75, -208, -5), range(-255, 82, 10), range(-197, -107, 5), range(-45, 221, 8), range(4, 109, 5), range(-140, -24, 5), range(-93, 60, 11), range(-85, 181, 9))}, set(), {(range(250, 234, -3), range(-72, -77, -5), range(110, -84, -16), range(38, 173, 12), range(-165, -111, 3), range(-213, -255, -6), range(-160, 150, 11), range(197, 93, -14), range(-19, 97, 4), range(-136, -92, 10), range(42, -214, -1), range(19, 88, 8), range(124, 204, 8), range(-142, 208, 10), range(-139, 48, 5)), (range(86, -95, -3), range(16, -67, -15), range(-224, -39), range(39, 133, 2), range(-68, -160, -1), range(242, -52, -3), range(245, -71, -9), range(-28, 256, 9), range(-189, -199, -3)), (), (range(71, -194, -10), range(22, 241, 10), range(-123, -136, -13), range(-91, -199, -4), range(215, 109, -3), range(25, -84, -11), range(204, 132, -9), range(247, 93, -13), range(182, 223, 8), range(-225, -139, 8), range(227, -26, -13), range(-115, -190, -7), range(-98, -92, 2), range(115, -86, -15)), (range(131, -28, -15), range(241, 25, -15), range(20, 190, 6), range(124, 80, -11)), (range(246, 212, -5), range(220, -56, -15), range(235, 212, -11), range(-130, -181, -6), range(151, 74, -1), range(123, 22, -8), range(-78, -229, -12), range(-107, -116, -8), range(226, -160, -14), range(253, 194, -9)), (range(78, 162, 14), range(216, 217), range(170, 22, -12), range(11, 187, 14), range(134, 200, 5), range(252, -15, -12), range(-100, -192, -9), range(113, 117, 4), range(-183, 229, 4)), (range(-1, -247, -4), range(76, -211, -6), range(86, -168, -3), range(-231, 199), range(-154, -56, 12), range(157, 198, 13), range(241, 149, -12), range(-47, 175, 9), range(207, 106, -16)), (range(-166, 121, 11), range(-210, -54, 8), range(-189, 244, 6)), (range(211, 253, 6),), (range(192, -208, -15), range(-109, -116, -4), range(208, 90, -9), range(69, 4, -14), range(-190, 199, 3), range(115, -1, -10), range(-245, -139, 2), range(105, 188, 13), range(0, 43, 12), range(59, 149, 3), range(-116, 75, 11), range(201, 153, -1), range(-167, -218, -2), range(-173, 58, 14), range(4, -239, -9), range(-9, -218, -8)), (range(184, 176, -2), range(103, 4, -13), range(-87, 78, 8), range(-11, 216, 5))}, {(range(-160, -151, 2), range(-85, 30, 14), range(34, 3, -9), range(91, 151, 8), range(168, 191, 4), range(-200, -81, 3), range(53, 60, 7), range(-216, -83, 8), range(249, -6, -13), range(43, -29, -5), range(-34, -110, -6), range(-66, 244, 15), range(141, -78, -4), range(42, 103, 6)), (range(252, 236, -9), range(254, 256, 2), range(-183, -213, -7), range(187, 231, 9), range(192, -237, -9), range(81, -151, -9), range(230, -121, -14), range(120, -75, -5), range(140, 255, 9)), (range(195, -149, -5), range(65, -215, -13), range(194, 241, 12), range(118, 146, 6)), (range(-239, 130, 10), range(-171, 225, 14), range(111, 136, 8), range(-129, 201, 14), range(244, 253), range(70, 60, -10), range(30, -103, -13), range(43, 145, 15), range(-147, -13, 7), range(30, 238, 5), range(89, 116, 4)), (range(-24, 94, 13), range(-73, -115, -7)), (range(237, 147, -11), range(-200, 206), range(103, 102, -1), range(-102, 176, 9)), (range(-44, 104, 12), range(89, 136, 9), range(27, 8, -4), range(131, 192, 7))}, {(range(88, 6, -3), range(-219, 172, 13), range(229, 234, 5), range(-120, -15, 6), range(-27, 144, 15), range(-70, -59, 6), range(249, 237, -7)), (range(212, -106, -7), range(3, -31, -8), range(110, -41, -10), range(191, 224), range(213, -56, -6), range(236, -88, -5), range(229, 209, -2)), (range(169, -61, -14),), (range(-162, -148, 6), range(229, 235, 4), range(66, -22, -1), range(-189, -51, 10), range(170, -49, -2), range(235, 168, -12), range(154, 17, -5), range(4, 201, 8), range(233, 254, 15), range(247, 246, -1), range(235, 193, -5), range(165, -194, -5)), (range(-208, -251, -14), range(70, -65, -8), range(130, 216, 12), range(-107, -159, -2), range(167, -242, -9), range(184, 48, -6), range(-3, -85, -2), range(-210, 58, 7), range(54, 220, 9), range(139, -20, -6), range(-26, -61, -7), range(187, 156, -10)), (range(235, 249), range(8, -235, -1), range(49, -33, -2), range(217, 95, -3), range(84, 175, 7), range(209, 190, -3), range(155, 185, 13), range(46, 228, 3), range(49, 73, 4), range(205, 231, 8), range(171, 225, 14), range(-78, 79, 4)), (range(235, 128, -6), range(-59, 188), range(-218, 4, 9), range(249, 241, -7), range(-116, 82, 13), range(33, 166, 4), range(120, 143, 12), range(192, -33, -11), range(177, 140, -15), range(24, 115, 6), range(198, 227, 11), range(191, 248, 3), range(194, 174, -1), range(92, -169, -11), range(-199, 144, 9), range(204, -47, -12))}]
```

## Technologies and Capabilities

* Guess Testing is written in [Python 3.8](https://www.python.org/downloads/release/python-38/).
* Does not require any additional packages.
* Features a pretty progress bar for enhanced satisfaction.
* Very lightweight.
* Flexible guessing stop conditions, like full coverage (by lines and instructions), an exception is thrown, certain
  time has passed, call count limit is reached...
* Allows getting information by coverage, return values, and exceptions.
* Easily extendable.
* What more can I say? It's small, standalone, and can actually be of use.

## Documentation

The code is documented using [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) format.

I hope that it can answer whichever questions that may arise.

## Contributing

Feel free to contact me if you have any comments, questions, ideas, and anything else you think I should be aware of.
Also, tell me what legendary matches have been played with Chess, or how playing against Stockfish improved your
strategy, I'd love to know.

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
