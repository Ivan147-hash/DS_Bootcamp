class Research:
    def __init__(self):
        pass

    def file_reader(self):
        with open('data.csv', 'r') as inf:
            result = inf.read()
            return str(result)

if __name__ == '__main__':
    reader = Research()
    print(reader.file_reader())