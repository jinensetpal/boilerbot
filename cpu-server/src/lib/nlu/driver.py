#!/usr/bin/env python3

from .dangerous_clf import DangerousClassifierModule
from .sensitive_clf import SensitiveClassifierModule

from lib.utils import accumulate
import multiprocessing

multiprocessing.set_start_method('spawn', force=True)
functions = [DangerousClassifierModule(), SensitiveClassifierModule()]

def runner(module, state, query):
    return module.execute(state, query)

def execute(state, query):
    # multiprocessing fails; too many open files
    # with multiprocessing.Pool(processes=len(functions)) as pool:
    #     return accumulate(pool.starmap(runner, [(function, state, query) for function in functions]))
    return accumulate([function.execute(state, query) for function in functions])

if __name__ == '__main__':
    print(execute({'uid': '1234'}, 'hello boilerbot'))
