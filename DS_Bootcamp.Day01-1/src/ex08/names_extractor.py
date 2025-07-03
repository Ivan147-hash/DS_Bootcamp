import sys

def extractor(fail):
    try:
        with open(fail, 'r') as inf, open('employees.tsv', 'w') as ouf:
            ouf.write('Name\tSurname\tE-mail')
            for email in inf:
                info = ''
                for i in range(len(email)):
                    if email[i] == '@':
                        break
                    if email[i] == '.' and email[i] !='@':
                        info += '\t'
                    else:
                        info += email[i]
                ouf.write('\n' + info.title())
                ouf.write('\t' + email.strip())
    except FileNotFoundError:
        print(f'Fail {fail} not found.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        extractor(sys.argv[1])
    else:
        print('Invalid input')