"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    src = source
    code = ''
    while src.find('\n') != -1:
        line = src[0:src.find('\n')] + ' \n'
        src = src[src.find('\n')+1:]
        code += line[0:line.find(';')]
    if src.find(';') == -1: 
        code += src
    else:
        code += src[0:src.find(';')]

    out = []
    nospaces = code.split()
    for word in nospaces:
        end = []
        while word.find('(') == 0 or word.find(')') == 0:
            out += [word[0]]
            word = word[1:]
        while word[::-1].find('(') == 0 or word[::-1].find(')') == 0:
            end += [word[-1]]
            word = word[:-1]
        if word != '':
            out += [word]
        out += end[::-1]
    return out


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if tokens == []: return []
    if tokens[0] == ')':
        raise SyntaxError
    if tokens[0] != '(':
        try:
            return int(tokens[0]) if float(tokens[0]).is_integer() else float(tokens[0])
        except:
            return tokens[0]
    else:
        ans = []
        statement = tokens[1:-1]
        key = 0
        while key < len(statement):
            if statement[key] == '(':
                ans.append(parse(statement[key:key+find_paren(statement[key:])+1]))
                key += find_paren(statement[key:]) + 1
            else:
                ans.append(parse([statement[key]]))
                key += 1
    return ans


def find_paren(tokens, c=-1):
    count = c
    for index, token in enumerate(tokens):
        if token == '(':
            count += 1
        elif token == ')':
            if count < 0: raise SyntaxError
            if count == 0: return index
            count -= 1
    raise SyntaxError


def multiply(args):
    ans = 1
    for num in args:
        ans *= num
    return ans

def custom_reduc(f, arr):
    start = arr[0]
    for val in arr[1:]:
        if not f(start, val):
            return False
        start = val
    return True

bools = {True: '#t', False: '#f'}

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': multiply,
    '/': lambda args: args[0] if len(args) == 1 else args[0]/multiply(args[1:]),
    '=?': lambda args: bools[custom_reduc(lambda x, y: x == y, args)],
    '>': lambda args: bools[custom_reduc(lambda x, y: x > y, args)],
    '>=': lambda args: bools[custom_reduc(lambda x, y: x >= y, args)],
    '<': lambda args: bools[custom_reduc(lambda x, y: x < y, args)],
    '<=': lambda args: bools[custom_reduc(lambda x, y: x <= y, args)],
    #'and': lambda args: bools[custom_reduc(lambda x, y: x == '#t', args) and args[-1] == '#t'],
    #'or': lambda args: bools[not (args[0] == '#f' and custom_reduc(lambda x, y: y == '#f', args))],
    'not': lambda args: '#f' if args[0] == '#t' else '#t'
}


def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    #print(tree)
    if tree == []:
        raise EvaluationError
    if env == None:
        env = {}
        for op in carlae_builtins:
            env[op] = carlae_builtins[op]
    else:
        for op in carlae_builtins:
            if op not in env:
                env[op] = carlae_builtins[op]
    if type(tree) == float or type(tree) == int:
        return tree
    elif type(tree) == list:
        if tree[0] == 'define':
            if type(tree[1]) == list:
                func = evaluate(['define', tree[1][0], ['lambda', tree[1][1:], tree[2]]], env) #i luv python slicing
                return func
            env[tree[1]] = evaluate(tree[2], env)
            return env[tree[1]]
        elif tree[0] == 'lambda':
            def fn(args): 
                fn_env = {}
                for op in env:
                    fn_env[op] = env[op]
                for ind, param in enumerate(tree[1]):
                    fn_env[param] = args[ind]
                return evaluate(tree[2], fn_env)
            #fn_env[fn] = evaluate(fn, args?) ??????
            return fn
        elif tree[0] == 'if':
            if evaluate(tree[1], env) == '#t':
                return evaluate(tree[2], env)
            return evaluate(tree[3], env)
        elif tree[0] == 'and':
            return bools[custom_reduc(lambda x, y: evaluate(x) == '#t', tree[1:]) and evaluate(tree[1:][-1]) == '#t']
        elif tree[0] == 'or':
            return bools[not (custom_reduc(lambda x, y: evaluate(x) == '#f', tree[1:])) or evaluate(tree[1:][-1]) == '#t']
        else:
            if type(evaluate(tree[0], env)) != type(lambda x: x) and type(evaluate(tree[0], env)) != type(sum):
                raise EvaluationError
            func = evaluate(tree[0], env)
            params = list(map(lambda x: evaluate(x, env), tree[1:]))
            return evaluate(func(params), env)
    elif type(tree) == type(lambda x: x):
       return tree
    elif tree in env:
        return env[tree]
    if tree == '#f' or tree == '#t':
        return tree
    raise EvaluationError


def repl(env=None):
    inp = input('in> ')
    if inp == 'QUIT' or inp == 'q': exit()
    try:  
        out, env = result_and_env((parse(tokenize(inp))), env)
        print('  out> ' + str(out) + '\n')
    except Exception as e:
        print('   ' + e.__class__.__name__ + ': ' + str(e) + '\n')
    repl(env)

def result_and_env(tree, env=None):
    #print(tree)
    if env == None:
        env = {}
    return (evaluate(tree, env), env)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    repl()

