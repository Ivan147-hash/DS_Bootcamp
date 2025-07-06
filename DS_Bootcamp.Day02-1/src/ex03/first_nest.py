import sys

class Research:
    def __init__(self, filename):
        self.filename = filename
        self.calculat = self.Calculations()

    def file_reader(self, has_header = True):
        try:
            with open(self.filename, 'r') as inf:
                flag = 0
                result = inf.read()
                temp = result.split('\n')
                if has_header:
                    flag = 1
                if has_header and temp[0] != 'head,tail':
                    raise ValueError('Incorrect header')
                for i in range(flag, len(temp)):
                    if temp[i] != '0,1' and temp[i] != '1,0':
                        raise ValueError('Incorrect values')
                return [[int(elem) for elem in temp[i].split(',')] for i in range(flag, len(temp))]
        except FileNotFoundError:
            print(f"File {self.filename} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    class Calculations:
        def counts(self, data):
            eagle = 0
            tails = 0
            for i in range(len(data)):
                if data[i][0] == 1:
                    eagle += 1
                if data[i][1] == 1:
                    tails += 1
            return f"{eagle} {tails}"
        
        def Fractions(self, count):
            eagle = int(count.split()[0])
            tails = int(count.split()[1])
            sum = eagle + tails
            eagl_prob = eagle * float(100 / sum)
            tails_prob = tails * float(100 / sum)
            # print(eagl, tails)
            return f"{eagl_prob} {tails_prob}"


if __name__ == '__main__':
    if len(sys.argv) == 2:
        reader = Research(sys.argv[1])
        data = reader.file_reader()
        print(data)
        count = reader.calculat.counts(data)
        print(count)
        probability = reader.calculat.Fractions(count)
        print(probability)
    else:
        print('Invalid input')