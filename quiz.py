import os
import random
import re
from datetime import datetime

import pandas as pd
from tabulate import tabulate

import utils
import views
from client import db
from views import PrintStyle, getch


def make_selection(word_list, dict_priority):
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
        meaning_list.append(meaning)
    return meaning_list


def make_daily_test_set(date=datetime.today().strftime('%Y-%m-%d')):
    return db.get_test_word(date=date)


def run(word_list, rotation=1):
    select_code = ['A', 'B', 'C', 'D', 'E']
    os.system('clear')
    print('loading data')
    utils.update_shortcut()

    for num_rotation in range(rotation):
        sequence = word_list.index.tolist()
        random.shuffle(sequence)
        correct_list = []
        wrong_list = []
        correct = 0
        for count, index in enumerate(sequence):
            word = word_list.loc[index, 'name']

            correct_ans_value = word_list.loc[index, 'meaning']
            wrong_ans_pool = word_list.index.tolist()
            wrong_ans_pool.remove(index)
            wrong_ans = random.sample(wrong_ans_pool, 4)

            options = word_list.loc[wrong_ans, 'meaning'].tolist()
            options.append(correct_ans_value)

            random.shuffle(options)
            correct_ans_index = options.index(correct_ans_value)
            code_added_options = []
            for code, option in zip(select_code, options):
                code_added_options.append('. '.join([code, option]))
            os.system('clear')
            print(f'rotation:{num_rotation+1}/{rotation}, word: {count+1}/{len(sequence)}, '
                  f'correct: {correct}, incorrect: {count-correct}, '
                  f'accuracy: {int(correct/count*100) if count>0 else 0}%\n')
            print(f'{PrintStyle.BOLD}Q: {word}{PrintStyle.ENDC}\n')
            selected = select_option(code_added_options)
            if selected == correct_ans_index:
                ans_color = 'BLUE'
                correct_list.append(word)
                word_list.loc[index, 'score'] += 1
                correct += 1
            else:
                ans_color = 'RED'
                wrong_list.append(word)
            show_option(code_added_options, color=ans_color, selected=correct_ans_index)
            input()
        print(f'test_result - accuracy: {int(len(correct_list)/len(sequence)*100)}%')
    return word_list[word_list['score'] < rotation]


def show_option(options, init=False, selected=0, color='PINK'):
    print_option = []
    count_new_line = 0
    arrow_up_cnt = len(options)
    selected_color = {
        'PINK': PrintStyle.PINK,
        'RED': PrintStyle.RED,
        'BLUE': PrintStyle.BLUE,
    }

    for index, option in enumerate(options):
        option, added_line = views.separate_line(option)
        count_new_line += added_line
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


def select_dict():
    quiz_type = ['my_dictionary', 'hackers', 'park']
    select_type = select_option(quiz_type, return_type='value')
    if select_type == 'my_dictionary':
        dict_priority = ['hackers', 'park', 'shortcut']
        data = make_daily_test_set(select_date())
        data['meaning'] = make_selection(data[dict_priority + ['meaning']], dict_priority)
        data = data.drop(dict_priority, axis=1)
    elif select_type in ['hackers', 'park']:
        os.system("clear")
        day = input('TEST DAY:')
        data = pd.read_sql_query(
            f"""select name, meaning
            from {select_type}_dictionary
            where day = {day}
            """,
            db.CONN,
        )
    else:
        raise ValueError
    return data


if __name__ == '__main__':
    os.system('clear')
    _data = select_dict()
    while True:
        os.system('clear')
        _rotation = input('CYCLE:')
        try:
            _rotation = int(_rotation)
            break
        except:
            print('NOT A NUMBER!!')
            input()
    while len(_data) > 5:
        _data['score'] = [0] * len(_data)
        _data['meaning'] = [meaning.replace('\n', ' ') for meaning in _data['meaning']]
        print_data = _data[['name', 'meaning', 'score']].copy()
        print_data['meaning'] = [
            views.separate_line(text, max_text_len=30, indentation=4)[0] for text in print_data['meaning'].tolist()
        ]
        print(tabulate(
            print_data[['score', 'name', 'meaning']],
            showindex=False,
            headers=['맞은갯수', '단어', '의미'],
            tablefmt='grid'
        ))
        input()
        fail_list = run(_data, rotation=_rotation)
