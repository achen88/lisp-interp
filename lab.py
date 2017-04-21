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
        out += [word] + end[::-1]
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
    #print(tokens, len(tokens))
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

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': multiply,
    '/': lambda args: args[0] if len(args) == 1 else args[0]/multiply(args[1:])
}




def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if type(tree) == float or type(tree) == int:
        return tree
    elif type(tree) == list:
        return evaluate(carlae_builtins[tree[0]](tree[1:]))
    elif tree in carlae_builtins:
        return carlae_builtins[tree]
    raise EvaluationError


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    print(evaluate(['+', 2, 3]))
