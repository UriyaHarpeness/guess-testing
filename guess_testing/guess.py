from collections import defaultdict

import datetime
import logging
from typing import Callable, Dict, Iterable, Set, Tuple

from guess_testing import tracing, generators


def reduce_dicts(a: tracing.Lines, b: tracing.Lines):
    for k in a.keys() & b.keys():
        a[k].difference_update(b[k])
        if not a[k]:
            a.pop(k)


logger = logging.getLogger('guess-testing')


def guess(positional: Iterable[generators.Generator], keyword: Dict[str, generators.Generator], func: Callable,
          depth: int = float('inf'), limit: int = float('inf'), timeout: int = 10):
    lines = tracing.list_func_calls(func, depth)
    tracing.setup_tracing(func)

    i = 0
    start = datetime.datetime.now()
    while i < limit and (datetime.datetime.now() - start).total_seconds() < timeout:
        i += 1
        args = tuple(p() for p in positional)
        kwargs = {k: v() for k, v in keyword.items()}
        id_ = args + tuple(kwargs.values())
        if id_ not in tracing.RUNS:
            tracing.ID = id_
            try:
                func(*args, **kwargs)
            except:
                pass
            reduce_dicts(lines, tracing.RUNS[id_])
            if not lines:
                logger.debug(f'Hit all: %d/%d attempts, %f seconds.', i, limit,
                             (datetime.datetime.now() - start).total_seconds())
                break

    tracing.remove_tracing()


def set_cover(full: tracing.FlatLines, subsets: Dict[str, tracing.FlatLines]) -> Tuple[Set[str], tracing.FlatLines]:
    cases = set()

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


def flatten(d: tracing.Lines) -> tracing.FlatLines:
    flat = set()
    for func_name, lines in d.items():
        flat.update((func_name, line) for line in lines)
    return flat


def unflatten(s: tracing.FlatLines) -> tracing.Lines:
    unflat = defaultdict(set)
    for func_name, line in s:
        unflat[func_name].add(line)
    return unflat


def print_results(func: Callable, depth: int = float('inf')):
    lines = tracing.list_func_calls(func, depth)
    cases, missed = set_cover(flatten(lines), {c: flatten(l) for c, l in tracing.RUNS.items()})
    logger.info('All: %s.', lines)
    logger.info('Cases: %s.', cases)
    logger.info('Cover: %d.', len(flatten(lines) - missed))
    logger.info('Missed: %d.', len(missed))
    logger.info('Cover %%: %f.', 100 - (len(missed) / len(flatten(lines))) * 100)
    logger.info('Misses: %s.', unflatten(missed))
