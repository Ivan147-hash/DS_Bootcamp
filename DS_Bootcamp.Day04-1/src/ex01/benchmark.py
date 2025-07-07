import timeit

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

def compare_time(time1, time2, time3):
    res = []
    res.append(time1)
    res.append(time2)
    res.append(time3)
    return sorted(res)

def main():
    time1 = timeit.timeit(lambda: cycle_add(emails), number=900000)
    time2 = timeit.timeit(lambda: list_comprehension(emails), number=900000)
    time3 = timeit.timeit(lambda: map_add(emails), number=900000)
    sort_time = compare_time(time1, time2, time3)
    print(time1, time2, time3)
    if time1 < time2 and time1 < time3:
        print('it is better to use a loop')
        print(f'{sort_time[0]} vs {sort_time[1]} vs {sort_time[2]}')
    elif time2 < time1 and time2 < time3:
        print('it is better to use a list comprehension')
        print(f'{sort_time[0]} vs {sort_time[1]} vs {sort_time[2]}')
    else:
        print('it is better to use a map')
        print(f'{sort_time[0]} vs {sort_time[1]} vs {sort_time[2]}')

if __name__ == '__main__':
    main()