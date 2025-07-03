def data_types():
    a = 1                # int
    b = "Hello"          # str
    c = 3.14             # float
    d = True              # bool
    e = [1, 2, 3]        # list
    f = {"key": "value"} # dict
    g = (1, 2, 3)        # tuple
    h = {1, 2, 3}        # set

    types = [a, b, c, d, e, f, g, h]

    result = [type(el).__name__ for el in types]  # Используем списковое выражение
    print('[' + ', '.join(result) + ']') 

if __name__ == '__main__':
    data_types()