import copy
import datetime
import logging
from collections import defaultdict
from typing import Callable, Dict, Optional, Sequence, Set, Tuple, Union

from guess_testing.generators import Generator, TypingGeneratorFactory
from guess_testing.tracing import Tracer

Lines = Dict[str, Set[int]]

logger = logging.getLogger('guess-testing')


class StopConditions:
    FULL_COVERAGE = 1
    TIMEOUT = 2
    CALL_LIMIT = 4
    EXCEPTION_RAISED = 8


class Guesser:
    def __init__(self, funcs: Sequence[Callable], positional: Sequence[Generator] = (),
                 keyword: Dict[str, Generator] = None):
        self.tracer = Tracer(funcs)
        if keyword is None:
            keyword = {}
        if positional is () and keyword == {}:
            keyword = TypingGeneratorFactory.get_generators(funcs[0])
        self.positional = positional
        self.keyword = keyword
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

    def check_stop_conditions(self, stop_conditions: int, run_count: int, call_limit: int, execution_time: float,
                              timeout: float, missed_lines: Dict[str, Set[int]]) -> bool:
        if stop_conditions & StopConditions.CALL_LIMIT and run_count >= call_limit:
            logger.debug(f'Reached attempts limit: %d, breaking.', call_limit)
            return True
        if stop_conditions & StopConditions.TIMEOUT and execution_time >= timeout:
            logger.debug(f'Reached seconds limit: %d, breaking.', timeout)
            return True
        if stop_conditions & StopConditions.EXCEPTION_RAISED and 0 < run_count <= len(
                self.tracer.runs) and isinstance(self.tracer.runs[run_count - 1][1], Exception):
            logger.debug(f'Exception was thrown, breaking.')
            return True
        if stop_conditions & StopConditions.FULL_COVERAGE and len(missed_lines) == 0:
            logger.debug(f'Full coverage achieved: %d/%.0f attempts, %f seconds. breaking.', run_count, call_limit,
                         execution_time)
            return True
        return False

    def guess(self,
              stop_conditions: int = StopConditions.FULL_COVERAGE | StopConditions.TIMEOUT | StopConditions.CALL_LIMIT,
              call_limit: int = float('inf'), timeout: int = 10,
              suppress_exceptions: Union[Sequence[Exception], Exception] = ()) -> 'Guesser':
        start = datetime.datetime.now()
        self.run_arguments = []
        run_count = 0
        missed_lines = copy.deepcopy(self.tracer.scope)

        # todo: maybe in the future enforce uniqueness of cases, but for most cases this will just not be worth it.
        with self.tracer:
            while not self.check_stop_conditions(stop_conditions, run_count, call_limit,
                                                 (datetime.datetime.now() - start).total_seconds(), timeout,
                                                 missed_lines):
                args = tuple(p() for p in self.positional)
                kwargs = {k: v() for k, v in self.keyword.items()}
                self.tracer.run_id = run_count
                self.run_arguments.append((args, kwargs))

                try:
                    result = self.tracer.funcs[0](*args, **kwargs)
                except suppress_exceptions as exception:
                    result = exception

                self.tracer.runs[run_count] = (self.tracer.runs[run_count], result)

                Guesser.reduce_dicts(missed_lines, self.tracer.runs[run_count][0])
                run_count += 1

        return self

    def get_best_cover(self) -> Tuple[Set[str], Lines]:
        cases = set()

        scope = copy.deepcopy(self.tracer.scope)
        subsets = {run_id: copy.deepcopy(run_scope[0]) for run_id, run_scope in self.tracer.runs.items()}
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

    @property
    def coverage(self) -> Optional[dict]:
        if self.tracer.runs is None:
            return None

        cases, missed = self.get_best_cover()
        return dict(scope=dict(self.tracer.scope),
                    cases=[self.run_arguments[case] for case in cases],
                    lines_count=self.lines_length(self.tracer.scope),
                    covered_lines_count=self.lines_length(self.tracer.scope) - self.lines_length(missed),
                    missed_lines_count=self.lines_length(missed),
                    coverage=100 - (self.lines_length(missed) / self.lines_length(self.tracer.scope)) * 100,
                    missed_lines=dict(missed))

    def get_exception_location(self, exception: Exception) -> Optional[Tuple[str, int]]:
        location = None
        stack_trace = exception.__traceback__
        stack = [stack_trace.tb_frame]
        while stack_trace.tb_next:
            stack_trace = stack_trace.tb_next
            stack.insert(0, stack_trace.tb_frame)

        for frame in stack:
            if frame.f_code.co_filename in self.tracer.scope and \
                    frame.f_lineno in self.tracer.scope[frame.f_code.co_filename]:
                location = (frame.f_code.co_filename, frame.f_lineno)
                break

        return location

    @property
    def exceptions(self) -> Optional[dict]:
        if self.tracer.runs is None:
            return None

        exception_runs = {run_id: results for run_id, results in self.tracer.runs.items() if
                          isinstance(results[1], Exception)}

        by_type = {}
        by_location = {}
        by_location_and_type = {}
        locations = defaultdict(set)
        for run_id, exception_run in exception_runs.items():
            location = self.get_exception_location(exception_run[1])
            if type(exception_run[1]) not in by_type:
                by_type[type(exception_run[1])] = (self.run_arguments[run_id], self.tracer.runs[run_id][1])
            if location not in by_location:
                by_location[location] = (self.run_arguments[run_id], self.tracer.runs[run_id][1])
                if location is not None:
                    locations[location[0]].add(location[1])
            if (location, type(exception_run[1])) not in by_location_and_type:
                by_location_and_type[(location, type(exception_run[1]))] = (
                    self.run_arguments[run_id], self.tracer.runs[run_id][1])

        return dict(locations=dict(locations),
                    by_location=by_location,
                    types=set(by_type.keys()),
                    by_type=by_type,
                    by_location_and_type=by_location_and_type)

    @property
    def return_values(self) -> Optional[dict]:
        if self.tracer.runs is None:
            return None

        # Note: a function that returns an exception, will be considered like it has thrown the exception.
        return_runs = {run_id: results for run_id, results in self.tracer.runs.items() if
                       not isinstance(results[1], Exception)}

        by_type = {}
        by_value = {}
        by_type_and_value = {}
        for run_id, return_run in return_runs.items():
            if type(return_run[1]) not in by_type:
                by_type[type(return_run[1])] = (self.run_arguments[run_id], self.tracer.runs[run_id][1])
            if return_run[1] not in by_value:
                by_value[return_run[1]] = (self.run_arguments[run_id], self.tracer.runs[run_id][1])
            if (type(return_run[1]), return_run[1]) not in by_type_and_value:
                by_type_and_value[(type(return_run[1]), return_run[1])] = (
                    self.run_arguments[run_id], self.tracer.runs[run_id][1])

        return dict(values=set(by_value.keys()),
                    by_value=by_value,
                    types=set(by_type.keys()),
                    by_type=by_type,
                    by_type_and_value=by_type_and_value)
