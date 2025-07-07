import sys
import os
import psutil

def read_file_generator(file):
    try:
        with open(file, 'r') as inf:
            for line in inf:
                strip_line =  line.strip()
                if strip_line:
                    yield strip_line
    except FileNotFoundError:
            raise FileNotFoundError(f"File {file} not found.")
    except Exception as e:
            raise Exception(f"An error occurred: {e}")

def list_is_generator(generator):
    lines = []
    for line in generator:
        lines.append(line)
    return lines

def generator_to_line(file):
    return list_is_generator(read_file_generator(file))

def main():
    if len(sys.argv) == 2:
        lines = generator_to_line(sys.argv[1])
        for line in lines:
            pass
            
        usage = psutil.Process()
        print(f'Peak memory usage= {usage.memory_info().rss / (1024**3)} GB')
        print(f'User Mode Time + System Mode Time = {usage.cpu_times().user + usage.cpu_times().system}s')
    else:
         print('Invalid argument')


if __name__ == '__main__':
    main()