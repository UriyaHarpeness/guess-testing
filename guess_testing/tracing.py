import dis
import inspect
from collections import defaultdict
from sys import gettrace, settrace
from typing import Callable, Optional, Sequence, Set, Tuple


class Tracer:
    def __init__(self, funcs: Sequence[Callable]):
        self.funcs = funcs
        self.scope = defaultdict(set)
        for func in funcs:
            path, lines = self.get_func_scope(func)
            self.scope[path].update(lines)
        self.original_trace = None

    @staticmethod
    def get_func_scope(func: Callable) -> Tuple[str, Set[int]]:
        bytecode = dis.Bytecode(func)
        lines = {bytecode.first_line}
        lines.update(instruction.starts_line for instruction in bytecode if instruction.starts_line is not None)
        path = inspect.getsourcefile(func)
        return path, lines

    def trace(self, frame: 'frame', event: str, arg=None) -> Optional[Callable]:
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
        self.run_id = None
        self.runs = defaultdict(lambda: defaultdict(set))
        self.original_trace = gettrace()
        settrace(self.trace)

    def __exit__(self, exc_type, exc_val, exc_tb):
        settrace(self.original_trace)
