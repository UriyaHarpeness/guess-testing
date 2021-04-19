import dis
import inspect
from collections import defaultdict
from sys import settrace

from enum import Enum, EnumMeta
from typing import Callable, Dict, Optional, Set, Tuple

Lines = Dict[str, Set[int]]
FlatLines = Set[Tuple[str, int]]


def list_func_calls(func: Callable, depth: int = float('inf')) -> Lines:
    if depth == 0:
        return {}

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
    for func_name in func_names.copy():
        if not isinstance(func_name, str):
            continue

        f = None
        if func_name in func.__globals__:
            f = func.__globals__[func_name]
        elif getattr(func, '__self__', None) and getattr(getattr(func, '__self__'), func_name, None):
            f = getattr(getattr(func, '__self__'), func_name)
        if f is not None and not isinstance(f, (Enum, EnumMeta)) and not inspect.isclass(f):
            funcs.update(list_func_calls(f, depth - 1))

    funcs[func.__name__] = lines
    return funcs


ID = None
RUNS = defaultdict(lambda: defaultdict(set))
FUNCS = set()


def my_tracer(frame: 'frame', event: str, arg=None) -> Optional[Callable]:
    code = frame.f_code
    func_name = code.co_name
    if func_name not in FUNCS:
        return None

    line_no = frame.f_lineno
    RUNS[ID][func_name].add(line_no)
    return my_tracer


def reset_calls(func: Callable, depth: int = float('inf')):
    global FUNCS
    global RUNS
    global ID
    FUNCS = list_func_calls(func, depth)
    RUNS = defaultdict(lambda: defaultdict(set))
    ID = None


def setup_tracing(func: Callable):
    reset_calls(func)
    settrace(my_tracer)


def remove_tracing():
    settrace(None)
