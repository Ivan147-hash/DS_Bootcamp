class Must_read:
    with open('data.csv', 'r') as inf:
        result = inf.read()
        print(result)

if __name__ == '__main__':
    reader = Must_read()