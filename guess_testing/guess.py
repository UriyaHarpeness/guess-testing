from __future__ import annotations

import contextlib
import copy
import datetime
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Sized, Tuple, Type, Union

from guess_testing.tracing import Tracer
from guess_testing.typing_generators_factory import ParametersGenerators, TypingGeneratorFactory

# A definition for a type that describes files and their line numbers (and optionally opcodes offsets).
Lines = Union[Set[int], Set[Tuple[int, Tuple[int, int]]]]


class StopConditions:
    """
    Stop conditions to use for choosing and combining to set when to stop guessing.
    """

    FULL_COVERAGE = 1
    TIMEOUT = 2
    CALL_LIMIT = 4
    EXCEPTION_RAISED = 8


class Guesser:
    """
    A class for guessing parameters for a function until a criteria is met.

    Can be used for the following cases:
    1.  Finding the smallest set of parameters for getting a full coverage of a scope.
    2.  Finding the possible exceptions the code can throw and from where, and which arguments cause these behaviors.
    3.  Finding all the possible return values of a function, and which arguments cause them.
    4.  Any form of stress testing, analysing an unknown code, and many, many more cases.
    """

    logger = logging.getLogger('guess-testing')

    __slots__ = '__tracer', '__parameters_generators', '__run_arguments', '__runs_with_results'

    def __init__(self, funcs: Union[Sequence[Callable], Callable], trace_opcodes: bool = False,
                 parameters_generators: Optional[ParametersGenerators] = None):
        """
        Constructor.

        Args:
            funcs: The scope of the code to guess on, the first function is the entry point for the guesser.
            trace_opcodes: Whether to trace opcodes as well, the default coverage is measured by lines, this is more
                thorough.
            parameters_generators: The parameters generators for the func, if not given will be inferred from its
                typing.
        """
        self.__tracer = Tracer(funcs, trace_opcodes)
        if parameters_generators is None:
            parameters_generators = TypingGeneratorFactory.get_generators(self.__tracer.funcs[0])
        self.__parameters_generators = parameters_generators
        self.__run_arguments: List[Tuple[Iterable[object], Mapping[str, object]]] = []
        self.__runs_with_results: Dict[int, Tuple[Dict[str, Lines], object]] = {}

    @staticmethod
    def reduce_lines(to_reduce: Dict[Any, Set[Any]], reduce_by: Dict[Any, Set[Any]]):
        """
        Reduce a lines structure.
        Removes all the values existing in lines reduce_by from lines to_reduce.

        Args:
            to_reduce: The lines to reduce.
            reduce_by: The lines to reduce by.
        """
        for k in to_reduce.keys() & reduce_by.keys():
            to_reduce[k] -= reduce_by[k]
            if not to_reduce[k]:
                to_reduce.pop(k)

    @staticmethod
    def equalize_lines(to_equalize: Dict[Any, Set[Any]], equalize_by: Dict[Any, Set[Any]]):
        """
        Equalize a lines structure.
        Removes all the values that do not exist in lines equalize_by from lines to_equalize.

        Args:
            to_equalize: The lines to equalize.
            equalize_by: The lines to equalize by.
        """
        for k in set(to_equalize.keys()):
            if k not in equalize_by:
                to_equalize.pop(k)
                continue
            to_equalize[k] &= equalize_by[k]
            if not to_equalize[k]:
                to_equalize.pop(k)

    @staticmethod
    def lines_length(lines: Dict[Any, Sized]) -> int:
        """
        Get the length of a lines structure.

        Args:
            lines: The lines to get length for.

        Returns:
            The length of the lines.
        """
        return sum(len(line) for line in lines.values())

    def check_stop_conditions(self, stop_conditions: int, call_count: int, call_limit: Union[float, int],
                              execution_time: float, timeout: float, missed_lines: Dict[str, Set[int]]) -> bool:
        """
        Check if any stop condition is met.

        Args:
            stop_conditions: The stop conditions to check.
            call_count: Call count.
            call_limit: Call limit.
            execution_time: Execution time of the function.
            timeout: Execution time limit.
            missed_lines: Lines not covered.

        Returns:
            Was any of the stop conditions is met.
        """
        if stop_conditions & StopConditions.CALL_LIMIT and call_count >= call_limit:
            self.logger.debug('Reached attempts limit: %d, breaking.', call_limit)
            return True
        if stop_conditions & StopConditions.TIMEOUT and execution_time >= timeout:
            self.logger.debug('Reached seconds limit: %d, breaking.', timeout)
            return True
        if stop_conditions & StopConditions.EXCEPTION_RAISED and 0 < call_count <= len(
                self.__runs_with_results) and isinstance(self.__runs_with_results[call_count - 1][1], Exception):
            self.logger.debug('Exception was thrown, breaking.')
            return True
        if stop_conditions & StopConditions.FULL_COVERAGE and len(missed_lines) == 0:
            self.logger.debug('Full coverage achieved: %d/%.0f attempts, %f seconds. breaking.', call_count, call_limit,
                              execution_time)
            return True
        return False

    def guess(self,
              stop_conditions: int = StopConditions.FULL_COVERAGE | StopConditions.TIMEOUT | StopConditions.CALL_LIMIT,
              call_limit: Union[float, int] = float('inf'), timeout: float = 10,
              suppress_exceptions: Union[Sequence[Type[Exception]], Type[Exception]] = (),
              pretty: bool = False) -> Guesser:
        """
        Guess arguments and call the entry function until any of the stop conditions is met.

        Args:
            stop_conditions: The stop conditions.
            call_limit: Call count limit.
            timeout: Execution time limit.
            suppress_exceptions: Exceptions to catch if thrown.
            pretty: Whether to display a pretty bar to visualize the guessing progress.

        Returns:
            The guesser.
        """
        self.__run_arguments = []
        call_count = 0
        missed_lines = copy.deepcopy(self.__tracer.scope)

        if pretty:
            from rich.progress import BarColumn, Progress, TimeElapsedColumn

        # todo: maybe in the future enforce uniqueness of cases, but for most cases this will just not be worth it.
        with self.__tracer, (Progress('[bold green]Guessing...[/bold green] [green]{task.description}', BarColumn(),
                                      '[purple]{task.percentage:>3.0f}%',
                                      TimeElapsedColumn())) if pretty else contextlib.suppress() as progress:
            prev_missed_lines_count = self.lines_length(missed_lines)
            if pretty:
                coverage = progress.add_task(str(call_count).ljust(8, ' '), total=prev_missed_lines_count)
            start = datetime.datetime.now()

            # Check stop conditions.
            while not self.check_stop_conditions(stop_conditions, call_count, call_limit,
                                                 (datetime.datetime.now() - start).total_seconds(), timeout,
                                                 missed_lines):
                # Prepare arguments.
                args = tuple(*self.__parameters_generators.positional, *self.__parameters_generators.var_positional())
                kwargs = dict(**self.__parameters_generators.var_keyword(),
                              **{k: v() for k, v in self.__parameters_generators.keyword.items()})

                self.__tracer.run_id = call_count
                self.__run_arguments.append((args, kwargs))

                try:
                    result = self.__tracer.funcs[0](*args, **kwargs)
                except suppress_exceptions as exception:
                    result = exception

                self.__runs_with_results[call_count] = (self.__tracer.runs[call_count], result)

                # Update coverage.
                Guesser.reduce_lines(missed_lines, self.__runs_with_results[call_count][0])
                call_count += 1

                missed_lines_count = self.lines_length(missed_lines)
                if pretty:
                    progress.update(coverage, advance=prev_missed_lines_count - missed_lines_count,
                                    description=str(call_count).ljust(8, ' '))
                prev_missed_lines_count = missed_lines_count

        return self

    def get_best_cover(self) -> Tuple[Set[int], Lines]:
        """
        Get the best coverage cases.

        Returns:
            The minimal set of cases to reach maximum coverage, and the lines that are not covered.
        """
        cases = set()

        scope = copy.deepcopy(self.__tracer.scope)
        subsets = {run_id: copy.deepcopy(run_scope[0]) for run_id, run_scope in self.__runs_with_results.items()}
        while scope:
            for subset in subsets.values():
                self.equalize_lines(subset, scope)
            subsets = {k: v for k, v in subsets.items() if len(v) > 0}
            if not subsets:
                break
            most_cover = max(subsets, key=lambda x: self.lines_length(subsets[x]))
            cases.add(most_cover)
            self.reduce_lines(scope, subsets[most_cover])

        return cases, scope

    @property
    def attempts_number(self) -> int:
        """
        Get the number of attempts that were run.

        Returns:
            The number of attempts that were run.
        """
        return self.__tracer.run_id if self.__tracer.run_id is None else self.__tracer.run_id + 1

    @property
    def coverage(self) -> Optional[dict]:
        """
        Get information summary related to coverage.

        Returns:
            Information summary related to coverage.
        """
        if not self.__runs_with_results:
            return None

        cases, missed = self.get_best_cover()
        return dict(scope=dict(self.__tracer.scope),
                    cases=[self.__run_arguments[case] for case in cases],
                    lines_count=self.lines_length(self.__tracer.scope),
                    covered_lines_count=self.lines_length(self.__tracer.scope) - self.lines_length(missed),
                    missed_lines_count=self.lines_length(missed),
                    coverage=100 - (self.lines_length(missed) / self.lines_length(self.__tracer.scope)) * 100,
                    missed_lines=dict(missed))

    def get_exception_location(self, exception: Exception) -> Optional[Tuple[str, int]]:
        """
        Get the source of an exception in the covered scope.

        Args:
            exception: The exception to get source for.

        Returns:
            The source of the exception in the covered scope.
        """
        location = None
        stack_trace = exception.__traceback__
        stack = [stack_trace.tb_frame]
        while stack_trace.tb_next:
            stack_trace = stack_trace.tb_next
            stack.insert(0, stack_trace.tb_frame)

        for frame in stack:
            if frame.f_code.co_filename in self.__tracer.scope and \
                    frame.f_lineno in self.__tracer.scope[frame.f_code.co_filename]:
                location = (frame.f_code.co_filename, frame.f_lineno)
                break

        return location

    @property
    def exceptions(self) -> Optional[dict]:
        """
        Get information summary related to exceptions.

        Returns:
            Information summary related to exceptions.
        """
        if not self.__runs_with_results:
            return None

        exception_runs = {run_id: results for run_id, results in self.__runs_with_results.items() if
                          isinstance(results[1], Exception)}

        by_type = {}
        by_location = {}
        by_location_and_type = {}
        locations = defaultdict(set)
        for run_id, exception_run in exception_runs.items():
            location = self.get_exception_location(exception_run[1])
            if type(exception_run[1]) not in by_type:
                by_type[type(exception_run[1])] = (self.__run_arguments[run_id], self.__runs_with_results[run_id][1])
            if location not in by_location:
                by_location[location] = (self.__run_arguments[run_id], self.__runs_with_results[run_id][1])
                if location is not None:
                    locations[location[0]].add(location[1])
            if (location, type(exception_run[1])) not in by_location_and_type:
                by_location_and_type[(location, type(exception_run[1]))] = (
                    self.__run_arguments[run_id], self.__runs_with_results[run_id][1])

        return dict(locations=dict(locations),
                    by_location=by_location,
                    types=set(by_type.keys()),
                    by_type=by_type,
                    by_location_and_type=by_location_and_type)

    @property
    def return_values(self) -> Optional[dict]:
        """
        Get information summary related to return values.

        Returns:
            Information summary related to return values.
        """
        if not self.__runs_with_results:
            return None

        # Note: a function that returns an exception, will be considered like it has thrown the exception.
        return_runs = {run_id: results for run_id, results in self.__runs_with_results.items() if
                       not isinstance(results[1], Exception)}

        by_type = {}
        by_value = {}
        by_type_and_value = {}
        for run_id, return_run in return_runs.items():
            if type(return_run[1]) not in by_type:
                by_type[type(return_run[1])] = (self.__run_arguments[run_id], self.__runs_with_results[run_id][1])
            if return_run[1] not in by_value:
                by_value[return_run[1]] = (self.__run_arguments[run_id], self.__runs_with_results[run_id][1])
            if (type(return_run[1]), return_run[1]) not in by_type_and_value:
                by_type_and_value[(type(return_run[1]), return_run[1])] = (
                    self.__run_arguments[run_id], self.__runs_with_results[run_id][1])

        return dict(values=set(by_value.keys()),
                    by_value=by_value,
                    types=set(by_type.keys()),
                    by_type=by_type,
                    by_type_and_value=by_type_and_value)
