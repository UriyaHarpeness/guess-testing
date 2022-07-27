import dis
from collections import defaultdict
from sys import gettrace, settrace
from typing import Callable, Dict, Optional, Sequence, Set, Tuple, Union


class Tracer:
    """
    A class for tracing execution of a specific scope.
    """

    __slots__ = '__original_trace', '__trace_opcodes', 'funcs', 'scope', 'runs', 'run_id'

    def __init__(self, funcs: Union[Sequence[Callable], Callable], trace_opcodes: bool = False):
        """
        Constructor.

        Args:
            funcs: The scope to trace.
            trace_opcodes: Whether to trace opcodes as well, the default coverage is measured by lines, this is more
                thorough.
        """
        self.__original_trace = None
        self.__trace_opcodes = trace_opcodes
        self.funcs = (funcs,) if callable(funcs) else funcs
        self.scope: Dict[str, Set[int]] = defaultdict(set)
        for func in self.funcs:
            path, lines, opcode_offsets = self.get_func_scope(func)
            self.scope[path].update(opcode_offsets if self.__trace_opcodes else lines)
        self.runs: Dict[int, Dict[str, Union[Set[int], Set[Tuple[int, Tuple[int, int]]]]]] = {}
        self.run_id = 0

    @staticmethod
    def get_func_scope(func: Callable) -> Tuple[str, Set[int], Set[Tuple[int, int]]]:
        """
        Get the scope of a function.

        Args:
            func: The function to get scope for.

        Returns:
            The file, lines, and opcode offsets inside the function's scope.
        """
        bytecode = dis.Bytecode(func)
        current_line = bytecode.first_line
        lines = {current_line}
        opcode_offsets = {(current_line, -1)}
        for instruction in bytecode:
            if instruction.starts_line:
                current_line = instruction.starts_line
                lines.add(current_line)
            opcode_offsets.add((current_line, instruction.offset))
        path = bytecode.codeobj.co_filename
        return path, lines, opcode_offsets

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
        if self.__original_trace is not None:
            self.__original_trace(frame, event, arg)

        code = frame.f_code
        filename = code.co_filename
        if filename not in self.scope:
            return None

        frame.f_trace_opcodes = self.__trace_opcodes
        opcode_offset = frame.f_lasti
        line_no = frame.f_lineno
        self.runs[self.run_id][filename].add((line_no, opcode_offset) if self.__trace_opcodes else line_no)
        return self.trace

    def __enter__(self):
        """
        Start tracing.
        """
        self.run_id = 0
        self.runs = defaultdict(lambda: defaultdict(set))
        self.__original_trace = gettrace()
        settrace(self.trace)

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: 'traceback'):
        """
        Stop tracing.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        settrace(self.__original_trace)
