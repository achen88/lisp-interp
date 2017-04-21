import sys

orig_recursion_limit = sys.getrecursionlimit()

import time
import importlib
import traceback

try:
    import lab
    importlib.reload(lab)
except ImportError:
    import solution
    lab = solution

if lab.sys.getrecursionlimit() != orig_recursion_limit:
    print(('WARNING: Recursion limit has been tampered with.  '
           'Resetting to original value of %d.') % orig_recursion_limit)
    lab.sys.setrecursionlimit(orig_recursion_limit)


def make_tester(func):
    def _tester(*args):
        try:
            return {'ok': True, 'output': func(*args)}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return {'ok': False, 'type': exc_type.__name__, 'exception': exc_obj.args}
    return _tester 

test_tokenize = lambda x: [make_tester(lab.tokenize)(i) for i in x]
test_parser = lambda x: [make_tester(lab.parse)(i) for i in x]
test_tokenize_and_parse = lambda sources: [make_tester(lambda i: lab.parse(lab.tokenize(i)))(source) for source in sources]
test_eval = lambda x: [make_tester(lab.evaluate)(i) for i in x]


def test_file_eval(*args):
    try:
        out = lab.evaluate_file(*args)
        return {'ok': True, 'output': out}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return {'ok': False, 'type': exc_type.__name__, 'exception': exc_obj.args}


def test_continued_evaluations(inps):
    env = None
    outs = []
    try:
        t = make_tester(lab.result_and_env)
    except:
        t = make_tester(lab.evaluate)
    for i in inps:
        if env is None:
            args = (i, )
        else:
            args = (i, env)
        out = t(*args)
        if out['ok']:
            env = out['output'][1]
        if out['ok']:
            if isinstance(out['output'][0], (int, float)):
                out['output'] = out['output'][0]
            else:
                out['output'] = 'SOMETHING'
        outs.append(out)
    return outs


def run_test(input_data):
    return globals()[input_data["function"]](*input_data["args"])
