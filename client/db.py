import sqlite3

import pandas as pd

from exceptions import NoResultError
from settings import NAVER_DICT_TYPE

DB_INFO = {
    'path': 'voca.db',
    'table': {
        '내단어장': 'my_dictionary',
        '박정': 'park_dictionary',
        '거만어': 'hackers_dictionary'
    },
}
CONN = sqlite3.connect(database=DB_INFO['path'], check_same_thread=False)


def execute_query(query):
    CONN.execute(query)
    CONN.commit()
    return CONN


def insert(_voca, _dict_meaning, source=NAVER_DICT_TYPE):
    if _dict_meaning:
        naver_dict = pd.DataFrame({
            'name': [_voca],
            'meaning': [_dict_meaning],
            'source': [source],
        })
        return naver_dict.to_sql(name=DB_INFO['table']['내단어장'], con=CONN, if_exists='append', index=False)
    else:
        raise NoResultError


def search(table=DB_INFO['table']['내단어장'], field=None, **kwargs):
    if len(kwargs) > 0:
        query_condition = ' where '
        query_condition += ' and '.join([f'{key}=\'{value}\'' for key, value in kwargs.items()])
    if field:
        field = ', '.join(field)
    else:
        field = '*'
    sql_query = f"select {field} from {table}{query_condition}"
    df = pd.read_sql_query(sql_query, CONN)
    return df


def delete(table=DB_INFO['table']['내단어장'], **kwargs):
    if len(kwargs) > 0:
        query_condition = ' where '
        query_condition += ' and '.join([f'{key}=\'{value}\'' for key, value in kwargs.items()])
    sql_query = f"delete from {table}{query_condition}"
    execute_query(sql_query)


def update(item_id):
    execute_query(
        f"""
        UPDATE {DB_INFO['table']['내단어장']}
        SET count= (
            CASE WHEN recent_search<>date('now', 'localtime')
            THEN count+1
            ELSE count
            END
        ), recent_search=date('now', 'localtime'), memorized='N'
        WHERE id={item_id}
        """
    )


def search_dictionary(dictionary_name, voca):
    data = search(table=DB_INFO['table'][dictionary_name], name=voca).replace('\n', ' ', regex=True)
    return f'{dictionary_name}: {data["meaning"][0]} - day{data["day"][0]}\n' if not data.empty else ''
