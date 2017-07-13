class NoResultError(Exception):
    def __init__(self):
        print('NO RESULT. PRESS ENTER')


class WrongTypeError(Exception):
    pass
