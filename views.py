import os


class PrintStyle:
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


def main(voca, dict_type, search_count, print_text, history, relevant_data):
    os.system("clear")
    print(
        f"WORD: {PrintStyle.BOLD}"
        f"{get_word_color(search_count)}"
        f"{voca}"
        f"{PrintStyle.ENDC}"
        f"{'*'*search_count}"
        f"{PrintStyle.ENDC}\n\n"
        f"{print_text}\n\n"
        f"REFERENCE: {dict_type}"
        f"{history}"
        f"{relevant_data}"
    )
