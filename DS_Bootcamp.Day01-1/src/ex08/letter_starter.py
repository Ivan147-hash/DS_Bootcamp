import sys

def starter(email):
    try:
        with open('employees.tsv', 'r') as inf:
            for info in inf:
                temp = info.split('\t')
                if email == temp[2].strip():
                    print(f'Dear {temp[0]}, welcome to our team. We are sure that it will be a pleasure to work withyou. That’s a precondition for the professionals that our company hires.')
    except FileNotFoundError:
        print(f'Fail employees.tsv not found.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        starter(sys.argv[1])
    else:
        print('Invalid input')