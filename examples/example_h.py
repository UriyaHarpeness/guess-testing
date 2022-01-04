from guess_testing.guess import Guesser


def h(a: int) -> str:
    return 'a' if a == 666 else 'b'


gg = Guesser(h, trace_opcodes=False)
gg.guess(call_limit=10000)
print(f'Attempts: {gg.attempts_number}, coverage: {gg.coverage["coverage"]}.')

gg = Guesser(h, trace_opcodes=True)
gg.guess(call_limit=10000)
print(f'Attempts: {gg.attempts_number}, coverage: {gg.coverage["coverage"]}.')
