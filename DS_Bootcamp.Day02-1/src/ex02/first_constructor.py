import sys

class Research:
    def __init__(self, filename):
        self.filename = filename

    def file_reader(self):
        try:
            with open(self.filename, 'r') as inf:
                result = inf.read()
                temp = result.split('\n')
                if temp[0] != 'head,tail':
                    raise ValueError('Incorrect header')
                for i in range(1, len(temp)):
                    if temp[i] != '0,1' and temp[i] != '1,0':
                        raise ValueError('Incorrect values')

                return str(result)
        except FileNotFoundError:
            print(f"File {self.filename} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 2:
        reader = Research(sys.argv[1])
        print(reader.file_reader())
    else:
        print('Invalid input')