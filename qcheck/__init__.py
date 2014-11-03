from __future__ import print_function
import collections
import itertools
import random
import string
import sys


Spec = collections.namedtuple('Spec', 'instance model actions properties')
Action = collections.namedtuple('Action', 'callable args kwargs')


def signature(*args, **kwargs):
    def decorator(func):
        func._args = [generator() for generator in args]
        func._kwargs = dict(
            (name, generator()) for name, generator in kwargs.items())
        return func
    return decorator


def random_action(spec, instance, model):
    action = random.choice(spec.actions)
    args = [next(generator) for generator in action._args]
    kwargs = dict(
        (name, next(generator))
        for name, generator in action._kwargs.items())
    return Action(action, args, kwargs)


def test_step(spec, instance, model, action=None):
    if action is None:
        action = random_action(spec, instance, model)
    try:
        retval = action.callable(
            instance, model, *action.args, **action.kwargs)
    except Exception as exc:
        return action, exc
    if retval is NotImplemented:
        return NotImplemented, None
    for prop in spec.properties:
        try:
            prop(instance, model)
        except Exception as exc:
            return action, exc
    return action, None


def reduce_test_case(spec, test_case):
    print('Reducing the test case')
    for seq_len in range(1, len(test_case) - 1):
        print('Checking test cases of length %d...' % (seq_len,))
        for sub_case in itertools.combinations(test_case, seq_len):
            instance = spec.instance()
            model = spec.model()
            for action in sub_case:
                retval, exc = test_step(spec, instance, model, action)
                if exc:
                    return sub_case
    return test_case


def generate_test_case(spec, max_length):
    test_case = []
    instance = spec.instance()
    model = spec.model()
    while len(test_case) < max_length:
        action = NotImplemented
        while action is NotImplemented:
            action, exc = test_step(spec, instance, model)
        test_case.append(action)
        if exc:
            print('ERROR:', repr(exc))
            test_case = reduce_test_case(spec, test_case)
            print('Failing case:')
            for action in test_case:
                print(
                    '%s %r %r' % (
                        action.callable.__code__.co_name,
                        action.args, action.kwargs))
            return test_case


def test_spec(spec):
    for test_len in range(30):
        for test_no in range(200):
            test_case = generate_test_case(spec, test_len)
            if test_case:
                return test_case


def rand_int(value_min=0, value_max=sys.maxint, edge_cases=[0, 1, 2]):
    for value in edge_cases:
        yield value
    while True:
        yield random.randint(value_min, value_max)


def rand_string(min_length=0, max_length=255, alphabet=None, edge_cases=['']):
    for value in edge_cases:
        yield value
    if alphabet is None:
        alphabet = string.ascii_letters + string.ascii_digits
    while True:
        yield ''.join(
            random.choice(alphabet)
            for i in range(random.randrange(min_length, max_length)))
