import os
import sqlite3

import pandas as pd

from exceptions import NoResultError
from settings import NAVER_DICT_TYPE, ROOT_DIR

DB_INFO = {
    'path': os.path.join(ROOT_DIR, 'voca.db'),
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


def insert(term, definition, shortcut, source=NAVER_DICT_TYPE):
    if definition:
        naver_dict = pd.DataFrame({
            'name': [term],
            'meaning': [definition],
            'source': [source],
            'shortcut': [shortcut]
        })
        return naver_dict.to_sql(name=DB_INFO['table']['내단어장'], con=CONN, if_exists='append', index=False)
    else:
        raise NoResultError


def search(table=DB_INFO['table']['내단어장'], field=None, **kwargs):
    if len(kwargs) > 0:
        query_condition = ' where '
        query_condition += ' and '.join([f'{key}=\'{value}\'' for key, value in kwargs.items()])
    else:
        query_condition = ''
    if field:
        field = ', '.join(field)
    else:
        field = '*'
    sql_query = f"select {field} from {table}{query_condition}"
    return pd.read_sql_query(sql_query, CONN)


def sort_by_date():
    return pd.read_sql_query(
        f"""SELECT recent_search, count(*) AS num_voca
            FROM my_dictionary
            GROUP BY recent_search
            ORDER BY recent_search DESC""",
        CONN
    )


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


def search_dictionary(dictionary_name, term):
    data = search(table=DB_INFO['table'][dictionary_name], name=term).replace('\n', ' ', regex=True)
    return f'{dictionary_name}: {data["meaning"][0]} - day{data["day"][0]}\n' if not data.empty else ''


def get_test_word(date=None):
    query = """
        SELECT A.name, A.meaning, A.shortcut AS shortcut, B.meaning AS hackers, C.meaning AS park
        FROM my_dictionary AS A
        LEFT JOIN hackers_dictionary AS B
        ON A.name = B.name
        LEFT JOIN park_dictionary AS C
        ON A.name = C.name
        """
    if date:
        query += f"WHERE a.recent_search = '{date}'"
    return pd.read_sql_query(query, CONN)


def save_shortcut(word, shortcut):
    execute_query(
        f"""
        UPDATE {DB_INFO['table']['내단어장']}
        SET shortcut = '{shortcut}'
        WHERE name='{word}'
        """
    )
