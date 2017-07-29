from datetime import datetime

import pandas as pd

import search
from client import db, quizlet, google


def get_data_from_quizlet(user_id, table_name):
    """
    박정 - user_id:'naeun_kim5', table_name :'gre_dictionary_1'
    거만어 - user_id: {'ilj0411', 'nintyning'}, table_name :'gre_dictionary_2'
    """

    data_table = pd.DataFrame(columns=['name', 'meaning', 'day'])
    name = []
    meaning = []
    index = []
    raw_data = quizlet.get_data(user_id)
    for day_data in raw_data:
        if day_data['title'].startswith('거만어 Day'):
            for term_info in day_data['terms']:
                name.append(term_info['term'].lower())
                meaning.append(term_info['definition'])
                index.append(''.join([s for s in day_data['title'] if s.isdigit()]))
    data_table['name'] = name
    data_table['meaning'] = meaning
    data_table['day'] = index
    data_table.to_sql(name=table_name, con=db.CONN, if_exists='append', index=False)


def make_test(start_day, end_day, num_term=25):
    a = pd.read_sql_query(
        f"""select name, meaning
        from park_dictionary
        where day BETWEEN {start_day}
        and {end_day}
        order by random()
        limit {num_term}""",
        db.CONN,
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
    for item in quizlet.get_data('yyc94'):
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


def save_shortcut(word):
    # shortcut = quizlet.get_shortcut(word)
    shortcut = google.search(word)
    db.execute_query(
        f"""
        UPDATE {db.DB_INFO['table']['내단어장']}
        SET shortcut = '{shortcut}'
        WHERE name='{word}'
        """
    )


def update_shortcut():
    word_list = pd.read_sql_query(
        "SELECT name FROM my_dictionary WHERE shortcut IS NULL", db.CONN
    )['name'].tolist()
    for index, word in enumerate(word_list):
        save_shortcut(word)
        print(f'{int((index+1)/len(word_list)*100)}%', end='\r')


def study_park(day):
    word_list = pd.read_sql_query(
        f"""select name
        from park_dictionary
        where day = {day}
        """,
        db.CONN,
    )['name'].tolist()
    for word in word_list:
        search.main(term=word)


if __name__ == "main":
    test_park()
