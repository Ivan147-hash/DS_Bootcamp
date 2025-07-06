# make_report.py
from config import step, temp_report, file_input, file_output
from analytics import Research

if __name__ == '__main__':
    reader = Research(file_input)
    data = reader.file_reader()
    if data != None:
        count = reader.calculat.counts()
        probability = reader.calculat.Fractions(count)
        predict = reader.analys.predict_random(step)
        heads_pred, tails_pred = tuple(sum(elem) for elem in zip(*predict))
        report = temp_report.format(len(data), count[2], count[0], float(probability[1]), float(probability[0]), step, tails_pred, heads_pred)
        reader.analys.save_file(report, file_output, 'txt')
    else:
        print("Empty file")