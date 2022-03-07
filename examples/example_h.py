from guess_testing.guess import Guesser


def h(a: int) -> str:
    return 'a' if a == 666 else 'b'


guesser = Guesser(h, trace_opcodes=False)
guesser.guess(call_limit=10000)
print(f'Attempts: {guesser.attempts_number}, coverage: {guesser.coverage["coverage"]}.')

guesser = Guesser(h, trace_opcodes=True)
guesser.guess(call_limit=10000)
print(f'Attempts: {guesser.attempts_number}, coverage: {guesser.coverage["coverage"]}.')
