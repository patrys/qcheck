#!/usr/bin/env python
from qcheck import rand_int, signature, Spec, test_spec

@signature(rand_int)
def array_push(instance, model, value):
    model.append(value)
    instance.append(value)


@signature()
def array_pop(instance, model):
    if not len(model):
        return NotImplemented
    expected = model.pop()
    returned = instance.pop()
    assert expected == returned, 'pop returned incorrect value'


@signature()
def array_len(instance, model):
    expected = len(model)
    returned = len(instance)
    assert expected == returned, 'len returned incorrect value'


class FaultyList(list):
    '''
    A nasty list implementation that only fails in rare cases
    '''
    def append(self, value):
        if len(self) < 6 or value % 17 != 11:
            return super(FaultyList, self).append(value)


array_spec = Spec(FaultyList, list, [array_len, array_pop, array_push], [])
test_spec(array_spec)
