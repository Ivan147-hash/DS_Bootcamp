import timeit
import random
from collections import Counter

def random_list(number):
    result = [random.randint(0, 100) for e in range(number)]
    return result

def dickt_my(list):
    result = {}
    for i in list:
        if i in result:
            result[i] += 1
        else:
            result[i] = 1
    return result

def my_top(list):
    dickt = counter_func(list)
    sorted_items = sorted(dickt.items(), key=lambda item: item[1], reverse=True)
    result = {}
    top = 10
    i = 0
    for key, value in sorted_items:
        if i < top:
            result[key] = value
        i += 1
    return result

def counter_func(list):
    result = Counter(list)
    return result

def counter_top(list):
    result = dict(Counter(list).most_common(10))
    return result

def main():
    number = 1000000
    list = random_list(number)
    time1 = timeit.timeit(lambda: dickt_my(list), number=10)
    print('my function:', time1)
    time2 = timeit.timeit(lambda: counter_func(list), number=10)
    print('Counter:', time2)
    timer3 = timeit.timeit(lambda: my_top(list), number=10)
    print('my top:', timer3)
    timer4 = timeit.timeit(lambda: counter_top(list), number=10)
    print('Counter\'s top:', timer4)

if __name__ == '__main__':
    main()