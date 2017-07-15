import os
import sys
import termios
import tty

import time

OPTION = {
    'ENTER': '계속',
    'PASS': '저장하지 않음',
    'EXAMPLE': '예문보기',
}


class PrintStyle:
    ARROW_UP = '\033[A'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_word_color(search_count):
    if search_count > 2:
        word_color = PrintStyle.RED
    elif search_count > 1:
        word_color = PrintStyle.GREEN
    else:
        word_color = ''
    return word_color


def input_voca():
    return input("ENTER WORD: ")


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def no_result():
    print(f'\nNO RESULT.\n\n{next_option()}')


def delete_option(voca):
    print(f'{PrintStyle.ARROW_UP}{PrintStyle.BLUE}word "{voca}" was deleted.{PrintStyle.ENDC}')
    time.sleep(0.5)


def wrong_option(option):
    error_message = f'{PrintStyle.ARROW_UP}{PrintStyle.RED}"{option}" was not determined.{PrintStyle.ENDC}'
    print(error_message, end="\r")
    time.sleep(1)
    print(' ' * len(error_message), end="\r")


def next_option(options=None):
    if options is None:
        options = []
    if 'ENTER' not in options:
        options.append('ENTER')
    return ', '.join(f'[{item}]: {OPTION[item]}' for item in options)


def exception(error):
    print(error)


def main(voca=None, dict_type=None, search_count=None,
         dict_meaning=None, history=None, relevant_data=None, options=None):
    os.system("clear")
    header = f"WORD: {PrintStyle.BOLD}{get_word_color(search_count)}{voca}{PrintStyle.ENDC}" \
             f"{'*'*(search_count if search_count >1 else 0)}{PrintStyle.ENDC}"
    body = f"{dict_meaning}"
    footer = f"REFERENCE: {dict_type}\n{history}{relevant_data}"
    print_text = f"{header}\n\n{body}\n{footer}\n\n{next_option(options)}\n"
    print(print_text)
