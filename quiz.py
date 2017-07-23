import os
import random
import re
from datetime import datetime

import utils
from client import db
from views import PrintStyle, getch

MAX_PRINT_LEN = 50


def make_data(word_list, dict_priority):
    meaning_list = []
    for index, row in word_list.iterrows():
        if row[dict_priority[0]]:
            meaning = row[dict_priority[0]]
        elif row[dict_priority[1]]:
            meaning = row[dict_priority[1]]
        elif row[dict_priority[2]]:
            meaning = row[dict_priority[2]]
        else:
            meaning = re.sub(r'(\*)(.*)(\n)', '', row['meaning']).replace('\n\n', '\n').replace('\n', ';')
        meaning_list.append(meaning.replace('\n', ''))
    word_list['selection'] = meaning_list
    word_list['score'] = [0] * len(word_list)
    return word_list


def make_daily_test_set(date=datetime.today().strftime('%Y-%m-%d')):
    return db.get_test_word(date=date)


def run(word_list, cycle=1, dict_priority=None):
    if dict_priority is None:
        dict_priority = ['hackers', 'park', 'shortcut']
    select_code = ['A', 'B', 'C', 'D', 'E']
    os.system('clear')
    print('loading data')
    utils.update_shortcut()
    make_data(word_list, dict_priority)

    for num_cycle in range(cycle):
        sequence = word_list.index.tolist()
        random.shuffle(sequence)
        correct_list = []
        wrong_list = []
        for count, index in enumerate(sequence):
            word = word_list.loc[index, 'name']

            correct_ans_value = word_list.loc[index, 'selection']
            wrong_ans_pool = word_list.index.tolist()
            wrong_ans_pool.remove(index)
            wrong_ans = random.sample(wrong_ans_pool, 4)

            options = word_list.loc[wrong_ans, 'selection'].tolist()
            options.append(correct_ans_value)

            random.shuffle(options)
            correct_ans_index = options.index(correct_ans_value)
            code_added_options = []
            for code, option in zip(select_code, options):
                code_added_options.append('. '.join([code, option]))
            os.system('clear')
            print(f'cycle:{num_cycle+1}/{cycle}, word: {count+1}/{len(sequence)}\n')
            print(f'{PrintStyle.BOLD}Q: {word}{PrintStyle.ENDC}\n')
            selected = select_option(code_added_options)
            if selected == correct_ans_index:
                ans_color = 'BLUE'
                correct_list.append(word)
                word_list.loc[index, 'score'] += 1
            else:
                ans_color = 'RED'
                wrong_list.append(word)
            show_option(code_added_options, color=ans_color, selected=correct_ans_index)
            input()
        print(f'test_result - accuracy: {int(len(correct_list)/len(sequence)*100)}%')
    return word_list[word_list['score'] < cycle]['score'].tolist()


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
                    new_line_text.append('\n\t')
                    make_new_line = False
                new_line_text.append(s)
            option = ''.join(new_line_text)
        if index == selected:
            option_color = selected_color[color]
        else:
            option_color = ''
        print_option.append(f'{option_color}{option}{PrintStyle.ENDC}')
        print_text = "\n".join(print_option)
    if init:
        position = ''
    else:
        position = PrintStyle.ARROW_UP * (arrow_up_cnt + count_new_line - 1)
    print(f'{position}{print_text}', end='\r')


def select_option(options, return_type='index'):
    index = 0
    show_option(options, init=True, selected=index)
    while True:
        selected = getch(option='UD')
        if selected == 'confirm':
            if return_type == 'value':
                return options[index]
            elif return_type == 'index':
                return index
            else:
                raise TypeError
        elif selected == 'up':
            index = (index - 1) if index > 0 else 0
        elif selected == 'down':
            index = (index + 1) if index < len(options) - 1 else len(options) - 1
        show_option(options, selected=index)


def select_date():
    data_by_date = db.sort_by_date()
    options = []
    for index, row in data_by_date.iterrows():
        options.append(f"{row['recent_search']}\t{row['num_voca']}")
    options.append('ALL DATE')
    print('date\t\tnum_voca')
    selected_index = select_option(options)
    if selected_index == len(data_by_date):
        return None
    else:
        return data_by_date.loc[selected_index, 'recent_search']


if __name__ == '__main__':
    os.system("clear")
    run(make_daily_test_set(select_date()))
