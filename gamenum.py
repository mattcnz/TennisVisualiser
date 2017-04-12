__author__ = 'mattmilliken'


import random
import math


def randArray():

    array = []
    for i in range(5):
        array.append(random.randint(1,5))
    return array

def performOp(a,b):
    operators = [
    'add',
    'minus',
    'times',
    'divide'
    ]

    op=operators[random.randint(0,3)]

    if op=='add':
        return a+b
    if op=='minus':
        return a-b
    if op=='times':
        return a*b
    if op=='divide' and a%b==0:
        return a/b
    else:
        performOpNoDiv(a,b)

def performOpNoDiv(a,b):
    operators = [
    'add',
    'minus',
    'times'
    ]
    op=operators[random.randint(0,2)]
    print op
    if op=='add':
        return a+b
    if op=='minus':
        return a-b
    if op=='times':
        return a*b


def allOps(arr):
    print arr
    current = performOp(arr.pop(), arr.pop())
    print current
    next = performOp(current,arr.pop())
    print next
    third = performOp(next,arr.pop())
    print third
    if len(arr)==1:
        return performOp(third,arr.pop())


arr = randArray()
print arr
first = performOp(arr[0],arr[1])
print first
second = performOp(first,arr[2])
print second
third = performOp(second,arr[3])

print third