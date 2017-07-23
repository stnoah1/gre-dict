import os
import random
import re
from datetime import datetime

import utils
from client import db
from views import PrintStyle, getch

MAX_PRINT_LEN = 50


def make_data(word_list):
    meaning_list = []
    for index, row in word_list.iterrows():
        meaning = re.sub(r'(\*)(.*)(\n)', '', row['meaning']).replace('\n\n', '\n')
        if row['hackers'] is not None:
            meaning = row['hackers']
        elif row['park'] is not None:
            meaning = row['park']
        elif row['shortcut'] != '':
            meaning = row['shortcut']
        else:
            meaning = meaning.replace('\n', ';')
        meaning_list.append(meaning.replace('\n', ''))
    word_list['selection'] = meaning_list
    return word_list


def test(day=datetime.today().strftime('%Y-%m-%d'), cycle=1):
    utils.update_shortcut()
    word_list = db.get_test_word(day)
    make_data(word_list)

    for num_cycle in range(cycle):
        sequence = word_list.index.tolist()
        random.shuffle(sequence)
        for count, index in enumerate(sequence):
            word = word_list.loc[index, 'name']

            correct_ans = word_list.loc[index, 'selection']
            wrong_ans_pool = word_list.index.tolist()
            wrong_ans_pool.remove(index)
            wrong_ans = random.sample(wrong_ans_pool, 4)

            options = word_list.loc[wrong_ans, 'selection'].tolist()
            options.append(correct_ans)

            random.shuffle(options)
            os.system('clear')
            print(f'cycle:{num_cycle+1}/{cycle}, word: {count+1}/{len(sequence)}\n')
            print(f'{PrintStyle.BOLD}Q: {word}{PrintStyle.ENDC}\n')
            selected = select_option(options)
            if selected == correct_ans:
                show_option(options, color='BLUE', selected=options.index(correct_ans))
            else:
                show_option(options, color='RED', selected=options.index(correct_ans))
            input()


def show_option(options, init=False, selected=0, color='PINK'):
    print_option = []
    count_new_line = 0
    make_new_line = False
    arrow_up_cnt = len(options)
    selected_color = {
        'PINK': PrintStyle.PINK,
        'RED': PrintStyle.RED,
        'BLUE': PrintStyle.BLUE,
    }

    for index, option in enumerate(options):
        if len(option) > MAX_PRINT_LEN:
            new_line_text = []
            for s_index, s in enumerate(option):
                if s_index > 0 and s_index % MAX_PRINT_LEN == 0:
                    make_new_line = True
                if make_new_line and s == ' ':
                    count_new_line += 1
                    new_line_text.append('\n')
                    make_new_line = False
                new_line_text.append(s)
            option = ''.join(new_line_text)
        if index == selected:
            option_color = selected_color[color]
        else:
            option_color = ''
        print_option.append(f'{option_color}[{option}]{PrintStyle.ENDC}')
        print_text = "\n".join(print_option)
    if init:
        position = ''
    else:
        position = PrintStyle.ARROW_UP * (arrow_up_cnt + count_new_line - 1)
    print(f'{position}{print_text}', end='\r')


def select_option(options):
    index = 0
    show_option(options, init=True, selected=index)
    while True:
        selected = getch(option='UD')
        if selected == 'confirm':
            return options[index]
        elif selected == 'up':
            index = (index - 1) if index > 0 else 0
        elif selected == 'down':
            index = (index + 1) if index < len(options) - 1 else len(options) - 1
        show_option(options, selected=index)


if __name__ == '__main__':
    test()
