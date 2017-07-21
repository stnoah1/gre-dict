import os
import sys
import termios
import tty

OPTION = {
    'PASS': '저장하지 않음',
    'ENTER': '계속',
    'DELETE': '삭제',
    'EXAMPLE': '예문보기',
    'BACK': '뒤로',
    'ENDIC': '영영사전',
    'KODIC': '한영사전',
}


class Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            input_key = sys.stdin.read(1)
            ch = (input_key + sys.stdin.read(2)) if input_key == '\x1b' else input_key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def getch(option='RL'):
    keymap = {
        'up': '\x1b[A',
        'down': '\x1b[B',
        'right': '\x1b[C',
        'left': '\x1b[D',
    }
    if option == 'Rl':
        option1 = 'left'
        option2 = 'right'
    elif option == 'UD':
        option1 = 'up'
        option2 = 'down'
    else:
        raise ValueError

    inkey = Getch()
    while True:
        k = inkey()
        if k != '':
            break
    if k == keymap[option2]:
        return option2
    elif k == keymap[option1]:
        return option1
    elif k == '\r':
        return 'confirm'
    elif k == '\x1b\x1b\x1b':
        exit(1)
    else:
        return None


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


def input_term():
    return input("ENTER WORD: ")


def no_result():
    print('\nNO RESULT.\n')
    show_option(['ENTER'])


def show_option(options, selected=0, update=False):
    print_option = []
    for index, item in enumerate(options):
        if index == selected:
            option_color = PrintStyle.PINK
        else:
            option_color = PrintStyle.BLUE
        print_option.append(f'{option_color}[{item}]{PrintStyle.ENDC}:{OPTION[item]}')
    print(f'\n{PrintStyle.ARROW_UP if update else ""}{"|".join(print_option)}', end='\r')


def select_option(options, default_option='ENTER'):
    if 'ENTER' not in options:
        options = ['ENTER'] + options
    index = options.index(default_option) if default_option in options else 0

    while True:
        show_option(options, selected=index, update=True)
        selected = getch()
        if selected == 'confirm':
            return options[index]
        elif selected == 'left':
            index = (index - 1) if index > 0 else 0
        elif selected == 'right':
            index = (index + 1) if index < len(options) - 1 else len(options) - 1


def exception(error):
    print(error)


def main(term=None, dict_type=None, search_count=None,
         definition=None, history=None, relevant_data=None):
    os.system("clear")
    header = f"WORD: {PrintStyle.BOLD}{get_word_color(search_count)}{term}{PrintStyle.ENDC}" \
             f"{'*'*(search_count if search_count >1 else 0)}{PrintStyle.ENDC}"
    body = f"{definition}"
    footer = f"REFERENCE: {dict_type}\n{history}{relevant_data}"
    print_text = f"{header}\n\n{body}\n{footer}\n"
    print(print_text)
