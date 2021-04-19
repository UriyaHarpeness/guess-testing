import dis
import inspect
from collections import defaultdict
from enum import Enum, EnumMeta
from sys import settrace
from typing import Callable, Dict, Optional, Set, Tuple

Lines = Dict[str, Set[int]]
FlatLines = Set[Tuple[str, int]]


class Tracer:
    def __init__(self, func: Callable, depth: int = float('inf')):
        self.func = func
        self.depth = depth
        self.lines = self.list_func_calls(func, depth)
        self.flat_lines = Tracer.flatten(self.lines)
        self.funcs = set(self.lines.keys())

    @staticmethod
    def list_func_calls(func: Callable, depth: int = float('inf'), encountered_func_names: Set[str] = None) -> Lines:
        if depth == 0:
            return {}
        if encountered_func_names is None:
            encountered_func_names = set()

        func_names = set()

        bytecode = dis.Bytecode(func)
        lines = {bytecode.first_line}

        instructions = list(reversed([instruction for instruction in bytecode]))
        for (ix, instruction) in enumerate(instructions):
            if instruction.starts_line is not None:
                lines.add(instruction.starts_line)
            if instruction.opname == 'CALL_FUNCTION':
                load_func_instruction = instructions[ix + instruction.arg + 1]
                func_names.add(load_func_instruction.argval)

        funcs = {}
        for func_name in func_names - encountered_func_names:
            if not isinstance(func_name, str):
                continue

            f = None
            if func_name in func.__globals__:
                f = func.__globals__[func_name]
            elif getattr(func, '__self__', None) and getattr(getattr(func, '__self__'), func_name, None):
                f = getattr(getattr(func, '__self__'), func_name)
            if f is not None and not isinstance(f, (Enum, EnumMeta)) and not inspect.isclass(f):
                funcs.update(Tracer.list_func_calls(f, depth - 1, set(*func_names, *encountered_func_names)))

        funcs[func.__name__] = lines
        return funcs

    def trace(self, frame: 'frame', event: str, arg=None) -> Optional[Callable]:
        code = frame.f_code
        func_name = code.co_name
        if func_name not in self.funcs:
            return None

        line_no = frame.f_lineno
        self.runs[self.run_id][func_name].add(line_no)
        return self.trace

    def __enter__(self):
        self.run_id = None
        self.runs = defaultdict(lambda: defaultdict(set))
        settrace(self.trace)

    def __exit__(self, exc_type, exc_val, exc_tb):
        settrace(None)

    @staticmethod
    def flatten(d: Lines) -> FlatLines:
        flat = set()
        for func_name, lines in d.items():
            flat.update((func_name, line) for line in lines)
        return flat

    @staticmethod
    def unflatten(s: FlatLines) -> Lines:
        unflat = defaultdict(set)
        for func_name, line in s:
            unflat[func_name].add(line)
        return unflat
