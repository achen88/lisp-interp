"""6.009 Lab 8B: carlae Interpreter Part 2"""

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
    #parse newlines to eliminate comments
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

    #split into words
    out = []
    nospaces = code.split()

    #separate parentheses
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
        #float/int
        try:
            return int(tokens[0]) if float(tokens[0]).is_integer() else float(tokens[0])
        #string
        except:
            return tokens[0]
    #is open paren
    else:
        cur = []
        #unbox
        find_paren(tokens)
        statement = tokens[1:-1]
        key = 0
        #recurseif paren, otherwise add to list
        while key < len(statement):
            if statement[key] == '(':
                cur.append(parse(statement[key:key+find_paren(statement[key:])+1]))
                key += find_paren(statement[key:]) + 1
            else:
                cur.append(parse([statement[key]]))
                key += 1
    return cur


def find_paren(tokens):
    """
    Helper to find the closing parenthesis given tokenized input. Returns index (int)

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    #number of closed and open paren should be equal
    count = 0
    for index, token in enumerate(tokens):
        if token == '(':
            count += 1
        elif token == ')':
            if count < 1:
             raise SyntaxError
            if count == 1: return index
            count -= 1
    raise SyntaxError


def multiply(args):
    """
    Definition of carlae mulitiplication.

    Arguments:
        args (list): a list of numbers to multiply
    """
    cur = 1
    for num in args:
        cur *= num
    return cur

def custom_reduc(f, arr):
    """
    Helper to model conditionals in carlae, with short circuiting

    Arguments:
        f (function): the function to test on values
        arr (list): list of values to be tested
    """
    start = arr[0]
    for val in arr[1:]:
        if not f(start, val):
            return False
        start = val
    return True


class LinkedList():
    """Class to represent lists in carlae, structured as a linked list"""

    def __init__(self, val):
        """
        Initializes LinkedList with given value

        Args:
            val (any): the value to initialize the head of the list to
        """
        self.elt = val
        self.next = None

    def append(self, val):
        """
        Creates and appends a node with given value to end of a LinkedList

        Args:
            self (LinkedList): LinkedList to append to
            val (any): value to be appended
        """
        self.next = LinkedList(val)

    def __repr__(self):
        """Representation of LinkedList for easier debugging, returns all values in a list"""
        return str(self.elt) + ' ' + str(self.next)


def listify(args):
    """
    Puts a list of arguments into a LinkedList, returning the respective head

    Args:
        args (list): list of values to be turned into a list
    """
    if args == []: return None
    head = LinkedList(args[0])
    cur = head
    for val in args[1:]:
        cur.next = LinkedList(val)
        cur = cur.next
    return head

def length(args):
    """
    Finds the length of a LinkedList

    Args:
        args (list): argument list, of which the first element is assumed to be a LinkedList
    """
    if args[0] == None: return 0
    if not isinstance(args[0], LinkedList): raise EvaluationError
    size = 1
    cur = args[0]
    while cur.next != None:
        cur = cur.next
        size += 1
    return size

def elt_at(args):
    """
    Find the i-th element in a LinkedList. Raises EvaluationError if index is out of bounds.

    args:
        args (list): argument list
            * 1st element: (LinkedList) list to look through, 
            * 2nd element: (int) index to go to
    """
    if args[0] == None: raise EvaluationError
    if not isinstance(args[0], LinkedList): raise EvaluationError
    cur = args[0]
    for i in range(args[1]):
        cur = cur.next
        if cur == None: raise EvaluationError
    return cur.elt

def concat(args):
    """
    Concatenates a series of LinkedLists, returning head of the first.

    Args:
        args (list): a list of LinkedLists
    """
    if args == []: return None
    #check for empty list
    first_not_empty = 0
    while args[first_not_empty] == None:
        first_not_empty += 1
        if first_not_empty == len(args): raise EvaluationError

    if not isinstance(args[first_not_empty], LinkedList): raise EvaluationError
    head = LinkedList(args[first_not_empty].elt)
    cur = head
    for lst in args:
        for i in range(length([lst])):
            cur.next = LinkedList(elt_at([lst, i]))
            cur = cur.next
    return head.next

def carlae_map(args):
    """
    Maps elements in a LinkedList with a given function.

    Args:
        args (list): a list with:
            * 1st element: (function) function to map with
            * 2nd element: (LinkedList) LinkedList to be mapped
    """
    fn = args[0]
    cur = args[1]
    if not isinstance(args[1], LinkedList): raise EvaluationError
    while cur != None:
        cur.elt = fn([cur.elt])
        cur = cur.next
    return args[1]

def carlae_filter(args):
    """
    Filters elements in a LinkedList with a given function.

    Args:
        args (list): a list with:
            * 1st element: (function) function to filter with
            * 2nd element: (LinkedList) LinkedList to be mapped
    """
    fn = args[0]
    cur = args[1]
    if not isinstance(args[1], LinkedList): raise EvaluationError
    head = None
    ans_cur = None
    while cur != None:
        if fn([cur.elt]) == '#t':
            if head == None:
                head = LinkedList(cur.elt)
                ans_cur = head
            else:
                ans_cur.next = LinkedList(cur.elt)
                ans_cur = ans_cur.next
        cur = cur.next
    return head

def carlae_reduce(args):
    """
    Reduces elements in a LinkedList with a given function and starting value.

    Args:
        args (list): a list with:
            * 1st element: (function) function to reduce with
            * 2nd element: (LinkedList) LinkedList to be mapped
            * 3rd element: (any) starting value to reduce with first element
    """
    fn = args[0]
    cur = args[1]
    if not isinstance(args[1], LinkedList): raise EvaluationError
    ans = args[2]
    while cur != None:
        ans = fn([ans, cur.elt])
        cur = cur.next
    return ans

#mapping of boolecur to carlae representations
bools = {True: '#t', False: '#f'}

#built-in functions
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
    #'and': see evaluate(), for short-circuit reasons
    #'or': see evaluate(), for short-circuit reasons
    'not': lambda args: '#f' if args[0] == '#t' else '#t',
    'list': listify,
    'car': lambda args: args[0].elt if args[0] != None else EvaluationError(),
    'cdr': lambda args: args[0].next if args[0] != None else EvaluationError(),
    'length': length,
    'elt-at-index': elt_at,
    'concat': concat,
    'map': carlae_map,
    'filter': carlae_filter,
    'reduce': carlae_reduce,
    'begin': lambda args: args[-1],
}

#list of tuples of (variable, environment) to keep track of where variables were binded for set! implementation
def_stack = []

def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    #base case
    if tree == []:
        raise EvaluationError
    #default env
    if env == None:
        env = {}
    #copy global env
    for op in carlae_builtins:
        if op not in env:
            env[op] = carlae_builtins[op]
    #primitives -- float, int, LinkedList ref, empty LinkedList, function, False boolean, True boolean
    if type(tree) == float or type(tree) == int or isinstance(tree, LinkedList) or tree == None or \
            type(tree) == type(lambda x: x) or tree == '#f' or tree == '#t':
        return tree
    #evaluate-able expression
    #check for keywords, then evaluate-able functions
    elif type(tree) == list:
        #define -> evaluate and store in env
        if tree[0] == 'define':
            if type(tree[1]) == list:
                func = evaluate(['define', tree[1][0], ['lambda', tree[1][1:], tree[2]]], env)
                return func
            env[tree[1]] = evaluate(tree[2], env)
            def_stack.append((tree[1], env))
            return env[tree[1]]
        #set! -> get lowest-level environment where variable was bound and change binding
        elif tree[0] == 'set!':
            first = list(filter(lambda x: x[0] == tree[1], def_stack[::-1]))
            #no variable definition anywhere
            if first == []: raise EvaluationError
            first = first[0]
            first[1][tree[1]] = evaluate(tree[2], env)
            return first[1][tree[1]]
        #lambda -> create function and return function object
        elif tree[0] == 'lambda':
            def fn(args): 
                #create function environment, inherits superenvironment
                fn_env = env.copy()
                #define variables as parameters
                for ind, param in enumerate(tree[1]):
                    fn_env[param] = args[ind]
                    def_stack.append((param, fn_env))
                return evaluate(tree[2], fn_env)
            return fn
        #if -> ternary statement
        elif tree[0] == 'if':
            if evaluate(tree[1], env) == '#t':
                return evaluate(tree[2], env)
            return evaluate(tree[3], env)
        #separate definitions for on-the-fly evaluation for short-circuiting purposes
        #cannot be built-ins because function calling preemptively evaluates all parameters
        elif tree[0] == 'and':
            return bools[custom_reduc(lambda x, y: evaluate(x, env) == '#t', tree[1:]) and evaluate(tree[1:][-1], env) == '#t']
        elif tree[0] == 'or':
            return bools[not (custom_reduc(lambda x, y: evaluate(x, env) == '#f', tree[1:])) or evaluate(tree[1:][-1], env) == '#t']
        #let -> create local environment for evaluation
        elif tree[0] == 'let':
            new_env = env.copy()
            #add one-time bindings and make note of
            for exp in tree[1]:
                new_env[exp[0]] = evaluate(exp[1], env)
                def_stack.append((exp[0], new_env))
            return evaluate(tree[2], new_env)
        #call function if not a keyword
        elif type(evaluate(tree[0], env)) == type(lambda x: x) or type(evaluate(tree[0], env)) == type(sum):
            func = evaluate(tree[0], env)
            params = list(map(lambda x: evaluate(x, env), tree[1:]))
            return evaluate(func(params), env)
        #keyword DNE & is not valid function
        raise EvaluationError
    #variable binding lookup
    elif tree in env:
        return env[tree]
    #undefined evaluation
    raise EvaluationError

def evaluate_file(file, env=None):
    """
    Evaluates carlae commands from file

    Args:
        file (string): filename with carlae commands
        env (dictionary) [optional]: environment to run commands in
    """
    f = open(file)
    if env == None:
        env = {}
    return evaluate(parse(tokenize(f.read())), env)

def repl(env=None):
    """
    read-eval-print-loop, feeds successive commands environment from previous command

    Arguments:
        env (dictionary): environment to run commands in
    """
    inp = input('in> ')
    if inp == 'QUIT' or inp == 'q': exit()
    #evaluate input given env
    try:  
        out, env = result_and_env((parse(tokenize(inp))), env)
        print('  out> ' + str(out) + '\n')
    #error
    except Exception as e:
        print('   ' + e.__class__.__name__ + ': ' + str(e) + '\n')
    repl(env)

def result_and_env(tree, env=None):
    """
    Evaluates statements given an environment. Returns the result of evaluation and environment.

    Arguments:
        tree (list): tree structure of expression
        env (dictionary): environment to run commands in
    """
    # print(tree)
    global def_stack
    # print(list(map(lambda x: x[0], def_stack)), env)
    # print('###\n\n\n')
    if env == None:
        env = {}
        def_stack = []
    val = evaluate(tree, env)
    return (val, env)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    #evaluate command line arguments and feed into global env
    if len(sys.argv) > 1:
        for file in sys.argv[1:]:
            evaluate_file(file, carlae_builtins)
    # env = {}
    repl()
