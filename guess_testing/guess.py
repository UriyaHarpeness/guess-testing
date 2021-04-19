import copy
import datetime
import logging
from typing import Callable, Dict, Iterable, Set, Tuple

from guess_testing.generators import Generator
from guess_testing.tracing import FlatLines, Lines, Tracer

logger = logging.getLogger('guess-testing')


class Guesser:
    def __init__(self, positional: Iterable[Generator], keyword: Dict[str, Generator], func: Callable,
                 depth: int = float('inf')):
        self.positional = positional
        self.keyword = keyword
        self.tracer = Tracer(func, depth)

    @staticmethod
    def reduce_dicts(a: Lines, b: Lines):
        for k in a.keys() & b.keys():
            a[k] -= b[k]
            if not a[k]:
                a.pop(k)

    def guess(self, limit: int = float('inf'), timeout: int = 10):
        missed_lines = copy.deepcopy(self.tracer.lines)
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
                    self.tracer.func(*args, **kwargs)
                except:
                    pass
                Guesser.reduce_dicts(missed_lines, self.tracer.runs[id_])
                if not missed_lines:
                    logger.debug(f'Hit all: %d/%f attempts, %f seconds.', runs, limit,
                                 (datetime.datetime.now() - start).total_seconds())
                    return

        if runs == limit:
            logger.debug(f'Reached attempts limit: %d, breaking.', limit)
            return

        logger.debug(f'Reached seconds limit: %d, breaking.', timeout)

    def get_best_cover(self) -> Tuple[Set[str], FlatLines]:
        cases = set()

        full = copy.deepcopy(self.tracer.flat_lines)
        subsets = {run_id: Tracer.flatten(lines) for run_id, lines in self.tracer.runs.items()}
        while full:
            for subset in subsets.values():
                subset &= full
            subsets = {k: v for k, v in subsets.items() if len(v) > 0}
            if not subsets:
                break
            most_cover = max(subsets, key=lambda sub: len(subsets[sub]))
            cases.add(most_cover)
            full ^= subsets[most_cover]

        return cases, full

    def print_results(self):
        cases, missed = self.get_best_cover()
        logger.info('All: %s.', self.tracer.lines)
        logger.info('Cases: %s.', cases)
        logger.info('Cover: %d.', len(self.tracer.flat_lines - missed))
        logger.info('Missed: %d.', len(missed))
        logger.info('Cover %%: %f.', 100 - (len(missed) / len(self.tracer.flat_lines)) * 100)
        logger.info('Misses: %s.', Tracer.unflatten(missed))
