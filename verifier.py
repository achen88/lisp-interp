import traceback

Number = (float, int)


def isiterable(x):
    try:
        for i in x:
            break
        return True
    except:
        return False


def check_same(x, y):
    if isinstance(x, str) and isinstance(y, str):
        return x == y
    xiter = isiterable(x)
    yiter = isiterable(y)
    if xiter and yiter:
        # if both are iterable, check elements within recursively
        xlist = list(x)
        ylist = list(y)
        return len(xlist)==len(ylist) and all(check_same(i,j) for i,j in zip(xlist, ylist))
    elif isinstance(x, Number) and isinstance(y, Number):
        # don't rely on float equality; just check if they're similar
        # 1e-9 is probably safe
        return abs(x-y) <= 1e-9
    else:
        return x == y  # fallback to good old equality here


def verify(result, inp, reference):
    out = []
    if inp['function'] == 'test_file_eval':
        result = [result]
        reference = [reference]
        inp['args'] = [inp['args']]
    for res, ref in zip(result, reference):
        try:
            message = "Good job! Everything looks fine."
            if res['ok'] and not ref['ok']:
                message = 'Your function should have raised an exception in this case.'
                ok = False
            elif ref['ok'] and not res['ok']:
                message = 'Your function should not have raised an exception in this case.'
                ok = False
            elif not (ref['ok'] or res['ok']):
                ok = ref['type'] == res['type']
                if not ok:
                    message = 'Your code raised a %s; expected a %s to be raised.' % (res['type'], ref['type'])
            else:
                ok = check_same(res['output'], ref['output'])
                if not ok:
                    message = 'Expected: %r\nGot: %r' % (ref['output'], res['output'])
            if inp['function'] in {'test_continued_evaluations', 'test_eval'} and not ok:
                message += '\nTry doing some testing (with this example or a related one) in the REPL.'
            out.append((ok, message))
        except:
            out.append((False, "Your code could not be verified :( Stack trace is printed here so you can debug:\n%s" % traceback.format_exc()))
    failed = [i for i in enumerate(out) if not i[1][0]]
    if len(failed) == 0:
        ok = True
        message = "Good job!  Everything looks fine."
    else:
        ok = False
        if len(failed) == 1:
            message = "One subtest failed:\n"
        else:
            message = "Some subtests failed:\n"
        message += '\n\n'.join(['Subtest: %r\n%s' % (inp['args'][0][i[0]], i[1][1]) for i in failed])
    return ok, message
