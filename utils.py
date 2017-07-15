from datetime import datetime

from client import db, quizlet
from client.quizlet import get_data


def get_data_from_quizlet(user_id, table_name):
    """
    박정 - user_id:'naeun_kim5', table_name :'gre_dictionary_1'
    거만어 - user_id: {'ilj0411', 'nintyning'}, table_name :'gre_dictionary_2'
    """
    import pandas as pd
    from client.db import CONN

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
    import pandas as pd
    from client.db import CONN

    return pd.read_sql_query(
        f"""select name, meaning
        from gre_dictionary
        where day BETWEEN {start_day}
        and {end_day}
        order by random()
        limit {num_term}""",
        CONN,
    ).to_csv(sep='\t', index=False)


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
