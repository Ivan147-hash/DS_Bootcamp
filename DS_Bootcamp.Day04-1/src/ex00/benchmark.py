import timeit

emails = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com', 'anna@live.com', 'philipp@gmail.com'] * 5


def cycle_add(emails_list):
    result = []
    for e in emails_list:
        result.append(e)
    return result

def list_comprehension(emails_list):
    result = [e for e in emails_list]
    return result

def main():
    time1 = timeit.timeit(lambda: cycle_add(emails), number=900000)
    time2 = timeit.timeit(lambda: list_comprehension(emails), number=900000)
    if time1 > time2:
        print('it is better to use a list comprehension')
        print(f'{time2} vs {time1}')
    else:
        print('it is better to use aloop')
        print(f'{time1} vs {time2}')


if __name__ == '__main__':
    main()