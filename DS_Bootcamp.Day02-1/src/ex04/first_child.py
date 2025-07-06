import sys
from random import randint

class Research:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.file_reader()
        self.calculat = self.Calculations(self.data)
        self.analys = self.Analytics(self.data)

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
        def __init__(self, data):
            self.data = data

        def counts(self):
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
            sum_val = eagle + tails
            eagl_prob = eagle * float(100 / sum_val)
            tails_prob = tails * float(100 / sum_val)
            return f"{eagl_prob} {tails_prob}"
        
    class Analytics(Calculations):
        def __init__(self, data):
            super().__init__(data)

        def predict_random(self, forecasts):
            predict = []
            for _ in range(forecasts):
                if randint(0, 1) == 1:
                    predict.append([1, 0])
                else:
                    predict.append([0, 1])
            return predict
        
        def predict_last(self):
            return self.data[-1]




if __name__ == '__main__':
    if len(sys.argv) == 2:
        reader = Research(sys.argv[1])
        data = reader.file_reader()
        if data != None:
            print(data)
            count = reader.calculat.counts()
            print(count)
            probability = reader.calculat.Fractions(count)
            print(probability)
            step = 3
            print(reader.analys.predict_random(step))
            print(reader.analys.predict_last())
        else:
            print("Empty file")
    else:
        print('Invalid input')