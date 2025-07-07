import sys
import os
import psutil

def read_file(file):
    try:
        with open(file, 'r') as inf:
            line = inf.readlines()
        return line
    except FileNotFoundError:
            raise FileNotFoundError(f"File {file} not found.")
    except Exception as e:
            raise Exception(f"An error occurred: {e}")

def main():
    lines = read_file(sys.argv[1])
    for line in lines:
        pass
    
    usage = psutil.Process()
    print(f'Peak memory usage= {usage.memory_info().rss / (1024**3)} GB')
    print(f'User Mode Time + System Mode Time = {usage.cpu_times().user + usage.cpu_times().system}s')

if __name__ == '__main__':
    main()