import copy
import datetime
import logging
from typing import Callable, Dict, Sequence, Set, Tuple

from guess_testing.generators import Generator, TypingGeneratorFactory
from guess_testing.tracing import Lines, Tracer

logger = logging.getLogger('guess-testing')


class Guesser:
    def __init__(self, funcs: Sequence[Callable], positional: Sequence[Generator] = (),
                 keyword: Dict[str, Generator] = None):
        self.tracer = Tracer(funcs)
        if positional is () and keyword is None:
            keyword = TypingGeneratorFactory.get_generators(funcs[0])
        self.positional = positional
        self.keyword = keyword
        self.cases = ()
        self.missed = {}
        self.run_arguments = []

    @staticmethod
    def reduce_dicts(a: Lines, b: Lines):
        for k in a.keys() & b.keys():
            a[k] -= b[k]
            if not a[k]:
                a.pop(k)

    @staticmethod
    def equalize_dicts(a: Lines, b: Lines):
        for k in a.keys() & b.keys():
            a[k] &= b[k]
            if not a[k]:
                a.pop(k)

    @staticmethod
    def lines_length(lines: Lines) -> int:
        return sum(len(l) for l in lines.values())

    def guess(self, limit: int = float('inf'), timeout: int = 10) -> 'Guesser':
        start = datetime.datetime.now()
        self.run_arguments = []
        run_count = 0
        missed_lines = copy.deepcopy(self.tracer.scope)

        # todo: maybe in the future enforce uniqueness of cases, but for most cases this will just not be worth it.
        with self.tracer:
            while run_count < limit and (datetime.datetime.now() - start).total_seconds() < timeout:
                args = tuple(p() for p in self.positional)
                kwargs = {k: v() for k, v in self.keyword.items()}
                self.tracer.run_id = run_count
                self.run_arguments.append((args, kwargs))

                try:
                    self.tracer.funcs[0](*args, **kwargs)
                except:
                    pass

                Guesser.reduce_dicts(missed_lines, self.tracer.runs[run_count])
                run_count += 1
                if len(missed_lines) == 0:
                    break

        self.cases, self.missed = self.get_best_cover()

        if len(missed_lines) == 0:
            logger.debug(f'Hit all: %d/%f attempts, %f seconds.', run_count, limit,
                         (datetime.datetime.now() - start).total_seconds())
            return self

        if run_count == limit:
            logger.debug(f'Reached attempts limit: %d, breaking.', limit)
            return self

        logger.debug(f'Reached seconds limit: %d, breaking.', timeout)

        return self

    def get_best_cover(self) -> Tuple[Set[str], Lines]:
        cases = set()

        scope = copy.deepcopy(self.tracer.scope)
        subsets = {run_id: run_scope for run_id, run_scope in self.tracer.runs.items()}
        while scope:
            for subset in subsets.values():
                self.equalize_dicts(subset, scope)
            subsets = {k: v for k, v in subsets.items() if len(v) > 0}
            if not subsets:
                break
            most_cover = max(subsets, key=lambda x: self.lines_length(subsets[x]))
            cases.add(most_cover)
            self.reduce_dicts(scope, subsets[most_cover])

        return cases, scope

    def print_results(self):
        logger.info('All: %s.', dict(self.tracer.scope))
        logger.info('Cases (%d): %s.', len(self.cases), [self.run_arguments[case] for case in self.cases])
        logger.info('Coverage: %d/%d (-%d) = %f%%.',
                    self.lines_length(self.tracer.scope) - self.lines_length(self.missed),
                    self.lines_length(self.tracer.scope), self.lines_length(self.missed),
                    100 - (self.lines_length(self.missed) / self.lines_length(self.tracer.scope)) * 100)
        logger.info('Misses: %s.', dict(self.missed))
