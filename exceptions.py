from views import no_result


class NoResultError(Exception):
    def __init__(self):
        no_result()


class WrongOptionError(object):
    def __init__(self):
        print("wrong option")
