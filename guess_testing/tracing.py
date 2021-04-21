import dis
import inspect
from collections import defaultdict
from sys import settrace
from typing import Callable, Dict, Optional, Set, Tuple

Lines = Dict[str, Set[int]]


class Tracer:
    def __init__(self, func: Callable):
        self.func = func
        self.scope = self.get_func_scope(func)

    @staticmethod
    def get_func_scope(func: Callable) -> Lines:
        bytecode = dis.Bytecode(func)
        lines = {bytecode.first_line}
        lines.update(instruction.starts_line for instruction in bytecode if instruction.starts_line is not None)
        path = inspect.getsourcefile(func)
        return {path: lines}

    def trace(self, frame: 'frame', event: str, arg=None) -> Optional[Callable]:
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
        settrace(self.trace)

    def __exit__(self, exc_type, exc_val, exc_tb):
        settrace(None)
