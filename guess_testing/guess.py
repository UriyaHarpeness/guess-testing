import copy
import datetime
import logging
from typing import Callable, Dict, Iterable, Set, Tuple

from guess_testing.generators import Generator
from guess_testing.tracing import Lines, Tracer

logger = logging.getLogger('guess-testing')


class Guesser:
    def __init__(self, positional: Iterable[Generator], keyword: Dict[str, Generator], funcs: Iterable[Callable]):
        self.positional = positional
        self.keyword = keyword
        self.tracer = Tracer(funcs)
        self.cases = ()
        self.missed = {}

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

    def guess(self, limit: int = float('inf'), timeout: int = 10):
        missed_lines = copy.deepcopy(self.tracer.scope)
        runs = 0
        start = datetime.datetime.now()
        with self.tracer:
            while runs < limit and (datetime.datetime.now() - start).total_seconds() < timeout:
                runs += 1
                args = tuple(p() for p in self.positional)
                kwargs = {k: v() for k, v in self.keyword.items()}
                id_ = args + tuple(kwargs.values())
                if id_ in self.tracer.runs:
                    continue
                self.tracer.run_id = id_
                try:
                    self.tracer.funcs[0](*args, **kwargs)
                except:
                    pass
                Guesser.reduce_dicts(missed_lines, self.tracer.runs[id_])
                if len(missed_lines) == 0:
                    break

        self.cases, self.missed = self.get_best_cover()

        if len(missed_lines) == 0:
            logger.debug(f'Hit all: %d/%f attempts, %f seconds.', runs, limit,
                         (datetime.datetime.now() - start).total_seconds())
            return

        if runs == limit:
            logger.debug(f'Reached attempts limit: %d, breaking.', limit)
            return

        logger.debug(f'Reached seconds limit: %d, breaking.', timeout)

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
        logger.info('Cases: %s.', self.cases)
        logger.info('Coverage: %d/%d (-%d) = %f%%.',
                    self.lines_length(self.tracer.scope) - self.lines_length(self.missed),
                    self.lines_length(self.tracer.scope), self.lines_length(self.missed),
                    100 - (self.lines_length(self.missed) / self.lines_length(self.tracer.scope)) * 100)
        logger.info('Misses: %s.', dict(self.missed))
