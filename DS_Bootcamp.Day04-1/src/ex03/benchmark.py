#!/usr/bin/env python3

import timeit
import sys
from functools import reduce

def loop_sum(step: int):
    sum = 0
    i = 1
    while(i <= step):
        sum += i*i
        i += 1
    return sum

def square_sum(x, i):
    return x + i * i

def reduce_sum(step: int):
    sum = reduce(square_sum, range(1, step + 1))
    return sum

def main():
    if len(sys.argv) == 4:
        try:
            step = int(sys.argv[3])
            iteration = int(sys.argv[2])
            if sys.argv[1] == 'loop':
                time1 = timeit.timeit(lambda: loop_sum(step), number=iteration)
                print(time1)
            elif sys.argv[1] == 'reduce':
                time2 = timeit.timeit(lambda: reduce_sum(step), number=iteration)
                print(time2)
            else:
                print('Incorrect parameter specified')
        except ValueError as e:
            print(f'Error is {e}')
    else:
        print('Invalid argument')

if __name__ == '__main__':
    main()
