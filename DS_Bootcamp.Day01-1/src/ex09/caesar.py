import sys

def coder(string, shift):
    result = []
    shift = int(shift)
    for char in string:
        if char.isalpha():
            char = (chr(ord(char) + shift))
            if ord(char) > 122:
                result.append(chr(ord(char) - 26))
            else:
                result.append(chr(ord(char)))
        else:
            result.append(char)
    ''.join(result)
    print(''.join(result))

def decoder(string, shift):
    result = []
    shift = int(shift)
    for char in string:
        if char.isalpha():
            char = (chr(ord(char) - shift))
            if ord(char) < 97:
                result.append(chr(ord(char) + 26))
            else:
                result.append(chr(ord(char)))
        else:
            result.append(char)
    ''.join(result)
    print(''.join(result))
    
if __name__ == '__main__':
    if len(sys.argv) == 4:
        if sys.argv[1] == 'encode':
            coder(sys.argv[2], sys.argv[3])
        if sys.argv[1] == 'decode':
            decoder(sys.argv[2], sys.argv[3])
    else:
        print('Invalid input')
