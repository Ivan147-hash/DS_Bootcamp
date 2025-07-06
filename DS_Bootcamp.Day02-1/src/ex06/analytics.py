# analytics.py
from random import randint
import logging
import requests

logging.basicConfig(
    filename='analytics.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,'
)

class Research:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.file_reader()
        self.calculat = self.Calculations(self.data)
        self.analys = self.Analytics(self.data)

    def file_reader(self, has_header = True):
        logging.info("Reading information from a file")
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
                logging.info(f"Read data from {self.filename}")
                return [[int(elem) for elem in temp[i].split(',')] for i in range(flag, len(temp))]
        except FileNotFoundError:
            print(f"File {self.filename} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_message(self, result = True):
        if result:
            message = "The report has been successfully created"
        else:
            message = "The report hasn’t been created due to an error"
        data = {
            'chat_id': '978245458',
            'text': message
        }
        response = requests.post('https://api.telegram.org/bot7955703793:AAEdnWXEjr5NNSLkU8sioDHxewMKWsbLe5w/sendMessage', json=data)
            
        if response.status_code == 200:
            print("Сообщение успешно отправлено")
        else:
            print("Ошибка при отправке сообщения:", response.text)

        
    class Calculations:
        def __init__(self, data):
            self.data = data

        def counts(self):
            logging.info("Calculating the counts of heads and tails")
            eagle = 0
            tails = 0
            for i in range(len(self.data)):
                if self.data[i][0] == 1:
                    eagle += 1
                if self.data[i][1] == 1:
                    tails += 1
            logging.info(f"Counts calculated: Heads = {eagle}, tails = {tails}")
            return f"{eagle} {tails}"
        
        def Fractions(self, count):
            logging.info("Сalculating the probability of heads or tails")
            eagle = int(count.split()[0])
            tails = int(count.split()[1])
            sum_val = eagle + tails
            eagl_prob = eagle * float(100 / sum_val)
            tails_prob = tails * float(100 / sum_val)
            logging.info(f"Probability of landing heads = {eagl_prob}, tails = {tails_prob}")
            return eagl_prob, tails_prob
        
    class Analytics(Calculations):
        def __init__(self, data):
            super().__init__(data)

        def predict_random(self, forecasts):
            logging.info("Predicting subsequent values")
            predict = []
            for _ in range(forecasts):
                if randint(0, 1) == 1:
                    predict.append([1, 0])
                else:
                    predict.append([0, 1])
            logging.info(f"Predicted values ​​for the next {forecasts} steps")
            return predict
        
        def predict_last(self):
            logging.info("Last throw")
            return self.data[-1]
        
        def save_file(self, report, file_output, extension):
            logging.info("Recording a report")
            with open(f'{file_output}.{extension}', 'w') as ouf:
                ouf.write(report)
            logging.info(f"The report is recorded in {f'{file_output}.{extension}'}")
