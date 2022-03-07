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
Any[str]
 \`^-e*	s"
Any[Set[bytes]]
{b">)nL2F!>Kwqm[#Ea'", b'}miy,z/s5%b.K!S}+%HIGE;', b'x+Xl}%]', b')Tv6*4!0bOiWTX \t@s5~th', b'\tng`cwihx }]AOG^+B+]aI%^<N'}
Any[range]
range(-106, 146, 3)
Any[Dict[range, Set[Tuple[bytes, Tuple[float, range, bytes, float, int, str, str, int], Optional[int], str, int, int, str, Optional[str], float, Union[bytes, float]]]]]
{range(142, 84, -13): {(b'Jed$hLGm*r<', (6061.102397463284, range(-182, 84, 5), b'f JZ2a\t`(T\t\t~#@gq\\BiXcppaL;', 59788.322449126455, -21382, 'vqs+EWF;MT', '>0KU^M`V6aY#_0ML7F!{Z@k', -36984), 65290, "!5&B~|I}3'(gyn", 61028, -48215, 'J,/D<^*', None, -34340.94111622384, 36318.84981154413), (b'M%OO"se9++L =zkI!NB6', (-45943.93015499736, range(-136, -250, -9), b'(G0w%8W', -49341.06623806014, -35119, "pw|\n'feBaA&y|Pm3En5qKlH", '_', 19407), None, '@,<}', -58973, -39676, 'M9B2#Y\\/&>SUhr{D]QX&@g', None, -6771.0225166350865, 17953.02869843178), (b'\n>Pq#WX%9j0cP\t\n[&69Na', (59756.45329086066, range(188, 18, -8), b'6%AwI\n^*J', 17843.915863410482, 37394, 'm', 'g-sg*P+zVf\\E}Xe-"E%AOA', 654), None, '/|MX', 13629, 20249, 'Vh5`k', None, -18457.706529832867, b' I\\hs|F"/G3x@=w/\\@ylod')}, range(-69, 51, 14): {(b'@hD3XG(mXyhOhhFIi`', (-48414.6792535391, range(206, 147, -6), b'6', -49660.2374652366, -16765, '\tiBEoIA8J|!', '#6|h5rZ^8jqJ8)4P/Y]3&\t\n^Z(0mUu ', -39067), 18580, '~O_Y>}m\\;', -41405, -49532, 'I\nre\\qk9Br', 'D7/!;%RvnK|.T|10PPd>zm\\2', 19229.08590640183, b"29w='-"), (b'8RKx\t+\nO*y6', (-23989.597098010956, range(-74, -180, -10), b'^l"', -27009.428944051397, -21856, "ji(R|;DJYu1L;`3P~'", 't6M]6\tKbA[YBM', 53320), 55584, 'zq `Jdgx', 58167, -42862, '3!Z#$=*9B9k2xo1yZR3bS5L k70', None, 1485.9038149998378, b'Fsp$A`*Lf>Bm\t'), (b'IHPrVA}r(X\n=sBJBRRCTbD6 r=', (-4270.938814840687, range(-156, -28, 9), b"E!N8&A*]'f+I.}vs K%vneRtl", -51874.38267907938, 59835, "'>#", '5^y}tV9', -40700), -24724, 'G-9sxOL&;-@<gX;%f(s\n~6Q1C)Nb8', 16441, -60863, '@ q)(o1tR^#.pWJ9mh', 'V|&Ku )pBDbKbYk^F', -56010.928772953805, b"Mh'.|(AG|\tAH pOSW+ 9UMZ~BRCF"), (b"R^.8]+P'x`&PL';^YC2D2e\tF&HYG$/", (55385.839622465704, range(-195, 247, 8), b'k,mRbA)am0B{iSQB;f0xyz.@1/', -58084.83839066779, 9638, 'jNo.A\\=hzv`', 'd-9wJgRu3/F)^6KNz"w3ld', -23142), None, 'l4T o]_QEodfDx`.L Ff/a])1GDfh*d', 14183, 37399, '[z', 'R0{S,MobrbL)JzF\\a-9qxgWi@', -53686.94791173827, -53906.83011259345)}, range(38, 173, 5): {(b'jWtS{B\t!!gw=5R', (-54625.96096071691, range(0, 17, 9), b'tSo[",oP=\\xZH1!I=i(^V~Hr_\tKg', 42414.37211844041, -36300, 'Sb}+1yGj', 'HSor."vtJ%pnrW9u2Gxt', 9253), 22162, 'n{1v}vZ-\n]]C/Q.|+%AL@SGh=q"yEl', 59251, -50410, 'hewbN5\tN$$>dHB3DXQes', '_X>@WCY5r>kZSK.4R#', -19080.31279827142, b'qa'), (b'utd|\n!gOM4!S\\cmGfVp&q', (-8911.45439566129, range(-88, 206, 14), b'];;rK&Z$~7A4_0OrbC)/UAkB0pd', 40567.294265301854, 16272, 'GDWQf+sv7', "'j\nJO)!^#V-Ci,@OXcb-F6", 34625), None, 'zK<Ut3]L6r@V`S>JT8|VLwf-7', -50911, -49434, '\tJ0s\tjt7aC"e$p^>q-!\'w VGTY**', '->Xbz', -51000.874039128335, b'W5_//J1b'), (b'{;_{#NwL', (51402.26074773303, range(83, 114, 11), b'jZ)]ze8qLGWs,%(ML/e"Vu\t2b.T', 25045.334653222963, 45764, '[DAfR8>xFnsl&', '%g=XmA3yKDn\\>GyJ1M=GctE', -25793), -58741, ']tCaMNlG0', -35997, -35653, '', None, -29895.7629650734, -5510.623280990272)}, range(197, -166, -10): {(b'2fl#\n4=~\n', (30838.544126882523, range(37, 53, 12), b'', -55626.15589803162, -2782, '+8z(@-byU|,y', 'H\t6Hym0t=tJ1;gB+")cc2~U7_N8', 435), 32374, "'64G6k5&/5;%GD\\4yw5QQa5W2", -59028, -7503, '@', None, 24283.372749339585, 6002.933190658208), (b'2li', (46742.049468635014, range(178, 135, -14), b'-gdV^W0rzESl', 45446.97718622832, -58056, 'O{_hiZXOH_tWDprcL', 'OCcDq9s@z{<)EaIzhQnrE=`.HSUltU"/', 18900), None, ')h&c^-]0 ."0#jALGy/^>4\'}x', -17091, 31195, "P{wr1k'>w", 'jep D\ti]c`<ofgs', -44788.92195243921, b"';aSfU%_Zi4m(a)Rj"), (b'@^3Q]{w0Zoh', (-32615.848080003692, range(-222, -48, 4), b'', -35338.69118396347, 38072, ')]b#hIy#HWsrK}m\nwbN\\mI#*rtn5', 'ck>_7\t/wy}+[0bozfe"xQ*wH+1KA3/', 13689), None, '|.\\[x00xhOyJP-~$BvE,^2', 36070, 50966, 'x-eW_si"H{=@@Lx@9%%{#X', 'H16X%0!', -65109.57009461633, b'8p*^r>6\\>p[9X'), (b'sl', (-35509.71250712419, range(-7, -161, -1), b'[0RzM p>]4AOZondIrqmY', 25750.749062151415, -50484, 'WW(IoG)d8wD_xthHj<POU0>q+IH\t%', 'iT7Iv55cDDrv^W', -5469), -50716, 'sY', 22768, -49621, 'qeo', None, -15570.433261305618, b'P!3N!66-o[&1+/t^M"{\n;1b^B'), (b'[\n6;2 }go$=', (56497.48271086576, range(-142, 240), b'zj&^\\IyeSJsuZvY2*r5M]re', 50083.99999237551, 1437, '+TZn.dt{i__4lwn,[jelk;', 'W+c#. AGztC33Wi,D)0H1HMCW{g7$Z', 46441), None, 'ph', -43120, 41448, '=Ia^vRQ[WhccJGvBNP@P7AiEguVNt&', 'O&', 41929.618576370514, b'|'), (b'94;_\tbnz2K1"-$<\t=A#ZrN', (-16749.2972131383, range(125, 180, 15), b"X(JNb-kL\n;FR+PnO&'uF(", 51769.409772379455, 50167, "`Um3LGN<Sf'N00", ';!}', 3763), 47024, 'w2Pf$E', -47775, 46368, "MotF#EFqt'Dr(&*Q-!FMO", '(O|CtB6\\#\'/"~sC7x""ER\tZ)f@', -13458.812261542887, -28230.012451079398), (b'R.AbcH$]8C,F"3,EkH$l', (23468.859113567785, range(-75, 16, 6), b'1tXsQ<33=k"BHFz"XAl^NH', -28062.275854534557, -24144, 'PW"cW#i+Fhsk4g6[-y9.>=X\n}9viq7t', 'k[j6qs08IHOLb&&qx.i5FTNo!q=[8d', -20080), None, 'zZxfWoY\nmT4pH!!\n', 45547, -41940, "!0{']", None, 32781.35939388593, b'}}RE#i)bIa~WCT#6-lKbyzGgI,)q=l')}, range(147, 228, 3): {(b'\n;x|k\\2+ma', (-19933.857194358017, range(189, 232, 14), b'DD\\i', 29013.955016102715, 12015, '| sOF^]Z&J~Pq_I', "2RqMGYqz8o;D*b'~F", 25288), 54822, 'fmsn+urhnS', -30117, -27204, '=0)wD6s`%u4', None, -18160.127657124118, 11247.066641066645), (b'--JwMT', (-21648.865442750757, range(225, -108, -4), b'%EKY8_qK}X\t=.}O`+Ng#2.98Z\\N4', 31314.398448628897, 43566, '8oHO\nu7tm5<b5dV3#Zs&<mo+s6ai', '!9ya&\\`mD$lr&),$Y', 7374), None, ' 5#*\n\nY@SDnE59k>n', -48489, -18715, 'yyTCuggF5G@3y+fli#s`>%0', None, -25822.68021834112, b'sBG*/ZV!I6scF.wxkZj4|GS|R/QBO'), (b"$Dc1#sa'mw9qfBVGc0a|ZcVk&HEjR#m", (54584.39088031152, range(-34, 5, 12), b'\'%,st4\n~"', -23698.59451198249, 30855, '"!5$bL GKh;\\P%', 'bP>\n@YiNwAq.~rd!', -25592), -10324, 'nz;O"', 26861, -62072, 's||+S$b@7dHPvQl6dWqS$Rux9F7', None, -6462.115152492843, -32528.548492490954), (b'#e$ZB/nIkzAlet', (-30999.013129800252, range(116, 42, -16), b'mJM @x#fG', 31996.133968443814, -982, 'ob', 'JaN;M7**7"Q!OvLLitK<=;6|<DvW|`J', 30425), 55321, 'AVMvpw&WxeK2_fMr}LwD$*JiL{oG0G2', 22323, -46320, '|MS23\n\tP ekW7C2{-hh0}CG', '', -4504.968661873834, 35408.66802173626), (b'Q@', (-51080.9769971449, range(160, 254, 10), b'qk#|c', -302.00565038113564, 45226, 'n;$,1w0D/MnkW_am{~~N', "81'$*58.I", 60489), -54847, 'vVm(_B$$,5XrbY1_6-5o+]9r\t~vtY,Kn', -1431, 30613, "'`}=\\^0RJqFs_\\Hh}t6l,", None, 25389.224618838794, b']V5C\n>KYJ%4uOtkF`,Pylzsjd'), (b'~s+c[l}$f\tgf"n]7O\'Bm]S2nlv\\=@n6{', (-28692.274939021387, range(222, 232, 8), b'zaYr/a";', -53008.522760568754, -48162, 'YQ6tf|. NaiD"GB}07-w F!t-20DZ3^', '\\TT7Zn5o~@+O\\9Jr )[,@d,S*', 26646), None, "Gb`+w4bgn=v'xgJiMrh&qGjMWAa1fJ<", -28890, -45994, "/_$ke4R'88gTc7b8SJBX1S0qtlV", None, -21393.30159639279, -34175.98580719603), (b'H.S', (27776.2094144063, range(-204, -194, 8), b')`1vn=\n)z+]~\nh8bRkgedB8@0\t2', 24587.63540395662, 36817, '_U+XE8Q', 'tfA\thqf[9LdBlSZ-6q$+5', 41603), None, "r#qp!wUrnEAQmV$ybIwA'6TCU|]Y$", 29596, 60627, '~CM"B(c%T><', None, -63082.10742114196, -15399.742436829576), (b"M.~*|~(.wV\n'7iF6TwjqOKe)i", (10915.796802950208, range(248, 198, -11), b"k5'f;>.K7dY", 6356.343347406888, 54569, ']/}', '"t*G6f5HHe\trtkLH*h', -30082), None, "\n6Z#87NI/d^i-]\n> T Q`XkK]|['.Rln", -5273, -14847, '3`lklM^]8(t$', 'I7);phLi.', -19236.815881414164, b'=&Mf#~.;\nlN\nk\\\tv-@skjjW*%Dc'), (b'Vx[]K8D<f', (-38568.605068380435, range(47, 230, 7), b"AP6V($'i\\Ja]3z\\$=y_*A", 18808.766096409614, 48090, ']H_y%', '', -32294), -61684, "naZ'f i\tAvH Jm92<gX&f", 27889, -51228, "Fc\tQDX'u$|[krCOz%.gm XW;N", None, 53309.05484556117, 32743.241303759612), (b"8F^SwOv4b-%FJY/HBP&'=cn8R\nOV|", (-61485.83843367016, range(-64, -205, -3), b"!'C8P}f6HQGUuE~\\]g|s#P{b((LY\\$", -36309.31550649446, 38054, 'JXN&FwWsFXAH', '\t&RVC4`g[U&)1Vd+!', -11547), 12744, 'N.[ZP', 23862, 39946, 'zCn\nBP4B3Is+zbk+<&[fC@Y/a$l', 'Y5mIhHYs`D', -49597.68713053333, -15871.954271176117), (b'MDQF)W', (-14362.799812386846, range(73, 208, 9), b".nOs'he", 2113.404012473926, -37452, 'g$E@*#~', 'fTlr.Pqx}-or,5T*A0^e+7rW', -45139), None, 'p%k}pp6', 54731, 48825, 'TyP}vMj-%P 2JwogE|"Zi5W', None, -30232.399958611393, b'ZBh6')}, range(76, 200, 14): {(b'k4urHPsvZ!L2]~=', (23631.676258783365, range(248, 56, -13), b'9', -46865.07703048218, 8890, 'o1ODV8<Dpxz{mt"aP#"u<', 'SC\tCdJ79\\\ncVK=pf', 53520), -37719, ' kT]3P>r\tCNRd&"_df^d[maA*\\M*~wq@', -32719, -11341, 'U', None, -19015.266575680667, b'Zp ,pB0rLE-\\8u[&;'), (b'in1abW`^*R_buON', (42573.445735579706, range(-217, -214, 2), b'usDroh]F<>6p&_}[zk]FxVSu[ %|Jae', 46649.74982854276, -13473, 'gltQIR_', 'Txqr#O==', 58125), -44727, '.VF', 4347, 1116, '\\', None, 2486.8884299673664, b'+C.dRx|5o\n~$}$Ftg"xQGJK#d'), (b'W47!na9@0CGJG<426Y$p-""3!T\'=', (-52117.988399096255, range(179, 122, -6), b'WohHoLu$<k<5', -28515.455708052075, 36372, 'Hm!g5X_t23^q*D5h= %vSXW(H=#F', '1jgU[5PR;5`_3/J0|"ESI-]9qqL', 37128), -61442, '&4/Ma[j 06<wxvtI"7}dP@;/qoeU8&N', 39348, 64294, 'm^S8\\99kvLoWIw<56,rGtGIjf$\n\t]YD', '!U7-ye KF`%Ol,#q,+4\n_P>)kQ', -27219.58269700197, -42536.255873737085), (b'>s"y_*z&W#(D', (-56693.4869867887, range(145, -69, -13), b'k4[', 48310.11188188453, 58048, 'EFED\ti', 'i*iN;y{(/dw.-i>*\nXVm8', -18055), 46672, 'V" $bSxgV%o`J$FiTuFK2gMgk<', 23715, 48548, '52;^{pn\'h"^LG5x^k"1dlx$GV,wOHK~', 'S$pkZ44$', -22734.52614520985, b'R'), (b",0_~%NT(G0(4Qi.%wC_'", (-13321.9667390143, range(14, 120, 15), b'T*Lk#!)NkNa*%O#>0L/J#f#p\\gys', 16749.447666725056, 23528, 'gNwI+PmpBX`-', 'YEL!#\\\'\nE.vsGv"', 22007), 59603, 'gl`H5*L', -3282, 59414, 'U]"!,p7j/Wj!&]\'#x]@p j!vmAp\'', None, -61332.0768587535, b'/ 9LF8'), (b'#,)_%9>VAtu`', (37655.630982279996, range(246, 233, -4), b'U{', -34512.461216433265, -64079, 't>H68yFh', 'k{Y ', 17726), 38382, 'NjogzzgBy[*]*K', 7686, -5845, 'igBr9HD*WDUke=h\nu3_1f!f', 'cuuRfBCU@^D,*Pvq=q2wiiH5Fj`Uh', 25750.328246073288, b'`eeJ18\nd<@$By_u7|{gN$^ EAU@)+3R'), (b'pn<VQ~', (-63767.705621233734, range(53, -86, -6), b'/"bp', -40624.090642747935, -50731, 'VwXN30raXp)1', 'Ry#lO\tUhD\td^cT', -18541), None, "gZ+s'3<jn-U58x/>uwaaf6CbZC,i5", -46126, 24410, "LaZ8j@,C|'{DtcLh8YyaQ8ldd", None, -9500.58804343034, b'N.7\\+SM($<,N"t0nt,pz@.l\t'), (b'|/S2NZ;|NuCNw(', (17295.092865168903, range(-51, 221, 4), b'aZ~ZC2((tPDhaLPz', -44634.92324800996, 20004, 'HcMX0', "-jxx))'mb){=&v>H", -34476), None, 's=qsb*/}Dk@N A', -6564, -46422, 'ez_i0', None, -53706.76079492936, -56732.593312654935), (b' ', (-32516.75569545648, range(200, 238, 12), b'\nh4o\\CBOPtOF1o', -38311.166323040015, -28159, ',xv/6ylyt', '%{{\nrp}oYzAxa#*a8aLu', 29321), 15598, 'C8xSYMie\tkh[;\\U', 64791, 31104, 'lh7$h<ms{`', None, 56037.65817250266, b''), (b')Zp-peH', (46174.271787239035, range(-16, -141, -7), b"'3zH'Henn~F672arh#t`u;", 39392.947528867924, 49912, 'dn\n.X\tl >09|x&', '5Ec*kc.FiRtCnoyEz1d^', -11383), -14656, '7u2aW=i2Yrzv^C~^VCDxW]xUP', 62464, 5498, 'A\\Bh=+bO@JJ~Pepd', None, -12101.567700187486, -15395.69988409555), (b"(Zj~'wOS2&9//\nB\n[g6", (-15367.81253511092, range(-75, -33, 15), b'0', 10416.215406712232, -21415, '7\tVB%(dh;YsZaMU', '\n#MF+%<(]US[_aBX"0K]*1vCI%j&!"te', -60611), None, '.cxv\n<J;(1#3ZA', 62060, -43313, "DF;Eh'", None, 8219.205245399557, b" l6V<GjHi\\wHm\t['V8\\]$ujt(\\|\nE"), (b'y^\\P9u> w>e56]{_<v87B5B ', (-26628.955812433313, range(80, 225, 8), b'{oc%W#9ivw]*-o', -50736.1937490315, 7438, '~R)SvQZI%6~', 'qn<@)oDb[`u,(ld', -22994), -6714, '3h\t|MA', 2989, -25082, '=Fn\\!kl3\\i1(D-XPR4', None, 32752.417676522018, b'bB2^{aSFqVLw')}, range(-35, 137): {(b'Y;srU3', (-24463.442538610674, range(208, 43, -5), b'bxVM;5E}SJcJKam', 35759.64960829314, -26361, "tL*X5c'", 'l Zu4"@UrtXg&%7', 46293), -23499, 'tdKGZ."', -18687, 6165, "P\\hk`AG3&'dgf`0<&7;v'6A{k^A${~&", '9zA;', 45471.756805740486, 977.3731568737858), (b'$vk!-mV+\\!%7\t{kF>$/PNz', (-1232.5792183574522, range(31, 26, -5), b'"m~\\vc(&y0)U)p$', -57014.71958769244, -50942, '_>}R,q)6`f0E&!]&x4', 'WrH3A7Vu!a<8TSsS\n;riZzy,)`_dW7', 42833), 24260, 'MAZTRRBkbOc', 2284, -57247, 'xy^2"j&VuHE>;Fs)SP', '8a8+c|NU', 59552.1172441409, -15132.27273881495), (b"R\nM3[1|'vPJ!\tp<19}CtN", (63286.01566570849, range(245, 184, -9), b'ui%V#ekVs~tHuYFfmNL"Snk', 33665.21534806733, 31015, 'ckr;O{{@', 'u"iQYxJ(Kf./{VM_F]5', 57720), None, '6NDo', -3589, -17436, 'H[~9$D=4\n(!OnN', None, 27146.499078221823, b'0kbXxNu'), (b"_`Onmk'S%+=", (38892.952465826515, range(197, 215, 5), b'0SA")n#%RKCos/%Y9dHFju7cN', -27493.065304241114, -20230, '-z!HWyFx z<\'"\\hvckY.\\Hk[1{j}H~5', "e{g!)'U>4)AHn3\t]D~", 1030), 54793, '4,[Gv%J|H$D21N$8,g\\8', 42625, 27843, '0&b\\DR-\t\nW)5noy1#G7X~.q', None, -22036.258589191144, b'afbGp'), (b'6 B\t/t', (-59598.26174451437, range(199, 198, -1), b'/CJKNXN"Ix/j}xCT[Q', -6618.055926226269, 21342, 's=INRD5', '\t|4$Nwqk7w.Rb$[CP>D{!Z-w[oNT4sc*', 61), None, 'VPI', -21532, 62550, "oqun&'O-j|!#q5jn\n.r3 ", None, 10604.55739242585, b'r)YG3,5xd$GIU6Q+xSro'), (b'#F{{i,E/5+6C!8yFRYIrhpkPZ,+]L}c', (33237.92799434591, range(-133, -211, -10), b"'oO^F2Kr4n&k", -42467.72773359447, 59516, '8]}f]bx', 'h', 24405), None, '', -65287, 52716, '"9]XXNTZ.Sg);[[\t@Id<~848a\ttBH%', '_K$eA8OP', -33194.36744397624, -56966.818012266085), (b'57\t=Y !%\t\tFY1w$g<', (-63934.855779690435, range(204, 114, -7), b'.=}rur7!(@yq~%*', -60213.90168755746, -20675, 'U*e;_n/.{KquA4kd%1^Y', '+]3aJx4}tX;n/\n7', 35386), 44904, 'hDF/Xc\n7{$ 2zsrC Vu^K^Zg_11YI#;~', -48560, 53685, 'v9/ibn0)eU-pPj', '+H+1ZlB6 uI-n_Y', -33517.0852678091, b'z&\n5vJ%S7xp\tys(g'), (b'J.mmBdB&SE-o\taz[RR"Ctrg6*f}', (-46115.22746326482, range(-82, 208, 3), b'k362V6[ZC', 11606.480007914943, 15619, 'J~_Qp"y{CL8aWye60nd[', '9U"C.Gn#W+kLcCA@!d', 24343), None, "MC(~+\n'HPJQuW-&}y]}LLm4/]", 869, -10173, 'FjAn', '^!R7O@*Y|^Bm;;i3{4', -55278.514886898236, 54310.09133847324)}}
Any[float]
-63836.00431433
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
* Contains a string representation for the generators that fits `typing` and the builtin python types.
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
