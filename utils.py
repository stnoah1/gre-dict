import os
import random
import re
from datetime import datetime

import pandas as pd

from client import db, quizlet
from client.db import CONN, DB_INFO
from client.quizlet import get_data, get_shortcut
from views import PrintStyle, getch


def get_data_from_quizlet(user_id, table_name):
    """
    박정 - user_id:'naeun_kim5', table_name :'gre_dictionary_1'
    거만어 - user_id: {'ilj0411', 'nintyning'}, table_name :'gre_dictionary_2'
    """

    data_table = pd.DataFrame(columns=['name', 'meaning', 'day'])
    name = []
    meaning = []
    index = []
    raw_data = get_data(user_id)
    for day_data in raw_data:
        if day_data['title'].startswith('거만어 Day'):
            for term_info in day_data['terms']:
                name.append(term_info['term'].lower())
                meaning.append(term_info['definition'])
                index.append(''.join([s for s in day_data['title'] if s.isdigit()]))
    data_table['name'] = name
    data_table['meaning'] = meaning
    data_table['day'] = index
    data_table.to_sql(name=table_name, con=CONN, if_exists='append', index=False)


def make_test(start_day, end_day, num_term=25):
    a = pd.read_sql_query(
        f"""select name, meaning
        from park_dictionary
        where day BETWEEN {start_day}
        and {end_day}
        order by random()
        limit {num_term}""",
        CONN,
    ).to_csv(sep='\t', index=False)
    print(a)


def convert_data(search_date=datetime.today().strftime('%Y-%m-%d'), conversion_type='quizlet', add_field=None):
    if add_field is None:
        add_field = []
    field = ['name', 'meaning', *add_field]
    voca_data_set = db.search(field=field, recent_search=search_date)
    if conversion_type == 'quizlet':
        data = {
            'terms': voca_data_set['name'].tolist(),
            'definitions': voca_data_set['meaning'].tolist()
        }
        return quizlet.create_set(f'gre-{search_date}', data)
    elif conversion_type == 'csv':
        return voca_data_set.to_csv(f'gre-{search_date}.csv')
    else:
        print('error')


def get_gre_voca_by_day(day):
    voca = pd.read_csv('data/gre_voca_by_day.csv')
    return voca[voca['Day'] == day]['Word.1'].tolist()


def synonyms():
    day_list = []
    term_list = []
    synms_list = []
    for item in get_data('yyc94'):
        day = ''.join(s for s in item['title'] if s.isdigit())
        for term in item['terms']:
            word = term['term']
            if 'syn)' in term['definition']:
                synms = term['definition'].split('syn)')[1].replace(' ', '')
            elif 'ex)' in term['definition']:
                synms = term['definition'].split('ex)')[1].replace(' ', '')
            else:
                synms = term['definition']
            day_list.append(day)
            term_list.append(word)
            synms_list.append(synms)

    data_table = pd.DataFrame()
    data_table['day'] = day_list
    data_table['term'] = term_list
    data_table['synoms'] = synms_list
    # exception 이 너무 많아 다 고려해야되나


def update_shortcut(word):
    shortcut = get_shortcut(word)
    shortcut = shortcut.replace('\r\n', ';') if '\r\n' in shortcut else shortcut
    shortcut = shortcut.replace('\r', ';') if '\r' in shortcut else shortcut
    shortcut = shortcut.replace('\n', ';') if '\n' in shortcut else shortcut
    print(PrintStyle.BOLD + word + PrintStyle.ENDC + '\n' + shortcut)
    db.execute_query(
        f"""
        UPDATE {DB_INFO['table']['내단어장']}
        SET shortcut = '{shortcut}'
        WHERE name='{word}'
        """
    )


def bulk_shortcut_update():
    word_list = pd.read_sql_query("SELECT name FROM my_dictionary WHERE shortcut IS NULL", CONN)['name'].tolist()
    print(word_list)
    for word in word_list:
        try:
            update_shortcut(word)
        except:
            print(word, 'error')


def test(day=datetime.today().strftime('%Y-%m-%d'), cycle=1):
    word_list = pd.read_sql_query(
        f"""SELECT A.name, A.meaning, A.shortcut as shortcut, B.meaning as hackers, C.meaning as park FROM my_dictionary AS A
        LEFT JOIN hackers_dictionary AS B
        ON A.name = B.name
        LEFT JOIN park_dictionary AS C
        ON A.name = C.name
        where a.recent_search = '{day}'""", CONN)
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

    for i in range(cycle):
        sequence = word_list.index.tolist()
        random.shuffle(sequence)
        for index in sequence:
            word = word_list.loc[index, 'name']

            correct_ans = word_list.loc[index, 'selection']
            wrong_ans_pool = word_list.index.tolist()
            wrong_ans_pool.remove(index)
            wrong_ans = random.sample(wrong_ans_pool, 4)

            options = word_list.loc[wrong_ans, 'selection'].tolist()
            options.append(correct_ans)

            random.shuffle(options)
            os.system('clear')
            print(f'{PrintStyle.BOLD}Q: {word}{PrintStyle.ENDC}\n')
            selected = select_option(options)
            if selected == correct_ans:
                continue
            else:
                show_option(options, ans=True, selected=options.index(correct_ans))
                input()


def show_option(options, init=False, selected=0, ans=False):
    print_option = []
    arrow_up_cnt = len(options)
    if ans:
        selected_color = PrintStyle.RED
    else:
        selected_color = PrintStyle.PINK

    for index, item in enumerate(options):
        if index == selected:
            option_color = selected_color
        else:
            option_color = ''
        print_option.append(f'{option_color}[{item}]{PrintStyle.ENDC}')
        print_text = "\n".join(print_option)
    if init:
        position = ''
    else:
        position = PrintStyle.ARROW_UP * (arrow_up_cnt - 1)
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
