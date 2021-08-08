import dis
import inspect
from collections import defaultdict
from sys import gettrace, settrace
from typing import Callable, Optional, Sequence, Set, Tuple, Union


class Tracer:
    """
    A class for tracing execution of a specific scope.
    """

    def __init__(self, funcs: Union[Sequence[Callable], Callable]):
        """
        Constructor.

        Args:
            funcs: The scope to trace.
        """
        self.funcs = (funcs,) if callable(funcs) else funcs
        self.scope = defaultdict(set)
        for func in self.funcs:
            path, lines = self.get_func_scope(func)
            self.scope[path].update(lines)
        self.original_trace = None
        self.runs = None
        self.run_id = None

    @staticmethod
    def get_func_scope(func: Callable) -> Tuple[str, Set[int]]:
        """
        Get the scope of a function.

        Args:
            func: The function to get scope for.

        Returns:
            The file and lines inside the function's scope.
        """
        bytecode = dis.Bytecode(func)
        lines = {bytecode.first_line}
        lines.update(instruction.starts_line for instruction in bytecode if instruction.starts_line is not None)
        path = inspect.getsourcefile(func)
        return path, lines

    def trace(self, frame: 'frame', event: str, arg=None) -> Optional[Callable]:
        """
        Trace function, the callback for each line execution.

        Args:
            frame: The frame that triggered the trace.
            event: The type of event that triggered the trace.
            arg: Additional argument.

        Returns:
            This trace function.
        """
        if self.original_trace is not None:
            self.original_trace(frame, event, arg)

        code = frame.f_code
        filename = code.co_filename
        if filename not in self.scope:
            return None

        line_no = frame.f_lineno
        self.runs[self.run_id][filename].add(line_no)
        return self.trace

    def __enter__(self):
        """
        Start tracing.
        """
        self.run_id = None
        self.runs = defaultdict(lambda: defaultdict(set))
        self.original_trace = gettrace()
        settrace(self.trace)

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: 'traceback'):
        """
        Stop tracing.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        settrace(self.original_trace)
