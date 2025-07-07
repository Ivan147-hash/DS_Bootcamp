import timeit
import sys

emails = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com', 'anna@live.com', 'philipp@gmail.com'] * 5


def cycle_add(emails_list: list[str]):
    result = []
    for e in emails_list:
        if e.lower().endswith('@gmail.com'):
            result.append(e)
    return result

def list_comprehension(emails_list):
    result = [e for e in emails_list if e.lower().endswith('@gmail.com')]
    return result

def map_add(emails_list):
    result = list(map(lambda e: e if e.lower().endswith('@gmail.com') else None, emails_list))
    return result

def filter_add(emails_list):
    result = list(filter(lambda e: e if e.lower().endswith('@gmail.com') else None, emails_list))
    return result

def main():
    if len(sys.argv) == 3:
        try:
            if sys.argv[1] == 'loop':
                time1 = timeit.timeit(lambda: cycle_add(emails), number=int(sys.argv[2]))
                print(time1)
            elif sys.argv[1] == 'list_comprehension':
                time2 = timeit.timeit(lambda: list_comprehension(emails), number=int(sys.argv[2]))
                print(time2)
            elif sys.argv[1] == 'map':
                time3 = timeit.timeit(lambda: map_add(emails), number=int(sys.argv[2]))
                print(time3)
            elif sys.argv[1] == 'filter':
                time4 = timeit.timeit(lambda: filter_add(emails), number=int(sys.argv[2]))
                print(time4)
            else:
                print('Incorrect parameter specified')
        except ValueError as e:
            print(f'Error is {e}')
    else:
        print('Invalid argument')

if __name__ == '__main__':
    main()