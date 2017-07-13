import os
import re
import sqlite3
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from collect_gre_data import create_set, add_to_quizlet
from collect_sentence import search_word, WrongWordError

DB_INFO = {
    'path': 'voca.db',
    'table': 'naver_dictionary',
    '박정': 'gre_dictionary1',
    '거만어': 'gre_dictionary2',
}

DICT_CSS_SELECTOR = {
    'oxford': 'div.box_wrap1.dicType_O',
    'donga': 'div.box_wrap1.dicType_D',
    'YBM': 'div.box_wrap1.dicType_U',
    'etc': 'div.box_wrap1_mar1',
}
CONN = sqlite3.connect(DB_INFO['path'])
NAVER_URL = {
    'base': 'http://endic.naver.com',
    'ajax': 'http://endic.naver.com/ajax_enkrEntry.nhn',
}
DEFAULT_DICT = 'oxford'
DICT_TYPE = 'oxford'


class PrintStyle:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class NoResultError(Exception):
    def __init__(self):
        print('NO RESULT. PRESS ENTER')


class WrongTypeError(Exception):
    pass


def data_request(_url):
    r = requests.get(_url)
    if r.status_code == 200:
        return r.text
    else:
        raise ConnectionError


def get_voca_url(_html, css_selector='dt.first > span > a'):
    bs = BeautifulSoup(_html, 'html.parser')
    try:
        first_result = bs.select_one(css_selector)
        _url = first_result.attrs['href']
        _voca = first_result.text
        return f'{NAVER_URL["base"]}/{_url}', _voca
    except:
        raise NoResultError


def request_voca(first_result):
    try:
        return data_request(first_result)
    except:
        raise NoResultError


def get_dict_data(_html, _dict_type=DEFAULT_DICT, sentence=False):
    bs = BeautifulSoup(_html, 'html.parser')
    results = bs.select(DICT_CSS_SELECTOR[_dict_type])
    dict_selector = DICT_CSS_SELECTOR.copy()

    while not results:
        dict_selector.pop(_dict_type)
        if not dict_selector:
            raise NoResultError
        _dict_type = list(dict_selector.keys())[0]
        results = bs.select(dict_selector[_dict_type])
    _dict_meaning = ''

    for result in results:
        _dict_meaning += ('*' + result.select_one('h3 > span.fnt_syn').text + '\n') \
            if result.select_one('h3 > span.fnt_syn') else ''
        for data in result.select('dl.list_a3 > *'):
            if str(data).startswith('<dt'):  # TODO: 이부분 더 좋은 방법으로 수정
                index = ''.join(s for s in data.select_one('span').text if s.isdigit())
                _dict_meaning += ''.join([index, '.']) if index else '-' + ' '
                _dict_meaning += ' '.join([item.text for item in data.select('em > span')])
                _dict_meaning += '\n'
            elif sentence and _dict_type == DEFAULT_DICT and str(data).startswith('<dd class="first'):
                _dict_meaning += PrintStyle.GREEN + \
                                 re.sub(r'(^\n\n)', '\tex) ', data.text).replace('\n\n', '\n\t    ') + \
                                 PrintStyle.ENDC

        _dict_meaning += '\n'
    return _dict_meaning, _dict_type


def save_data(_voca, _dict_meaning, source=DEFAULT_DICT):
    if _dict_meaning:
        naver_dict = pd.DataFrame({
            'name': [_voca],
            'meaning': [_dict_meaning],
            'count': [1],
            'source': [source],
        })
        return naver_dict.to_sql(name=DB_INFO['table'], con=CONN, if_exists='append', index=False)
    else:
        raise NoResultError


def search_db(table=DB_INFO['table'], field=None, **kwargs):
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


def update_db(item_id):
    CONN.execute(
        f"""
        UPDATE {DB_INFO['table']} 
        SET count= (
            CASE WHEN recent_search<>date('now', 'localtime') 
            THEN count+1 
            ELSE count 
            END
            ), recent_search=date('now', 'localtime'), memorized='N'
        WHERE id={item_id}
        """
    )
    CONN.commit()


def renew_html(_url, _dict_type):
    _html = request_voca(_url)
    bs = BeautifulSoup(_html, 'html.parser')
    css_id = f'#{DICT_CSS_SELECTOR[_dict_type].split(".")[-1]} > a'
    dict_tag = bs.select_one(css_id)
    if _dict_type != DEFAULT_DICT and dict_tag:
        _url = f'{NAVER_URL["ajax"]}?entryId={dict_tag.attrs["entryid"]}'
        _html = data_request(_url)
    return _html


def convert_data(search_date=datetime.today().strftime('%Y-%m-%d'), conversion_type='quizlet', add_field=None):
    if add_field is None:
        add_field = []
    field = ['name', 'meaning', *add_field]
    voca_data_set = search_db(field=field, recent_search=search_date)
    if conversion_type == 'quizlet':
        data = {
            'terms': voca_data_set['name'].tolist(),
            'definitions': voca_data_set['meaning'].tolist()
        }
        return create_set(f'gre-{search_date}', data)
    elif conversion_type == 'csv':
        return voca_data_set.to_csv(f'gre-{search_date}.csv')
    else:
        raise WrongTypeError


def get_word_color(search_count):
    if search_count > 2:
        word_color = PrintStyle.RED
    elif search_count > 1:
        word_color = PrintStyle.GREEN
    else:
        word_color = ''
    return word_color


def run(_voca, _dict_type, refine_voca=False):
    if refine_voca:
        _voca = search_word(_voca)
    url = f'{NAVER_URL["base"]}/search.nhn?sLn=kr&isOnlyViewEE=N&query={_voca}'
    first_url, _voca = get_voca_url(data_request(url))
    db_data = search_db(name=_voca)
    search_count = 1
    history = ''
    if db_data.empty:
        html = renew_html(first_url, _dict_type)
        _dict_meaning, _dict_type = get_dict_data(html, _dict_type)
        print_text, _ = get_dict_data(html, _dict_type, sentence=True)
        save_data(_voca, _dict_meaning, _dict_type)
    else:
        db_data = db_data.iloc[0].to_dict()
        _dict_meaning = db_data['meaning']
        _dict_type = db_data['source']
        search_count = db_data["count"] if db_data['recent_search'] == datetime.today().strftime('%Y-%m-%d') \
            else db_data["count"] + 1
        history = f'\nsearch_count: {search_count}회, recent_search: {db_data["recent_search"]}'
        update_db(db_data['id'])
        print_text = _dict_meaning
    os.system("clear")
    박정_db = search_db(table=DB_INFO["박정"], name=_voca).replace('\n', ' ', regex=True)
    거만어_db = search_db(table=DB_INFO["거만어"], name=_voca).replace('\n', ' ', regex=True)
    in_dictionary1 = f'\n박정: {박정_db["meaning"][0]} - day{박정_db["day"][0]} ' if not 박정_db.empty else ''
    in_dictionary2 = f'\n거만어: {거만어_db["meaning"][0]} - day{거만어_db["day"][0]}' if not 거만어_db.empty else ''
    print(
        f"WORD: {PrintStyle.BOLD}{get_word_color(search_count)}{_voca}{PrintStyle.ENDC}{'*'*search_count}"
        f"\n\n{print_text}\n"
        f"REFERENCE: {_dict_type}{history}{in_dictionary1}{in_dictionary2}"
    )
    add_to_quizlet(_voca, _dict_meaning)


if __name__ == '__main__':
    os.system("clear")
    while True:
        try:
            run(input("ENTER WORD: "), DICT_TYPE)
        except NoResultError:
            pass
        except ConnectionError as e:
            print(e)
            pass
        except WrongWordError:
            NoResultError()
        except BaseException as e:
            print(e)
        input()
        os.system("clear")
