import re

import requests
from bs4 import BeautifulSoup

from client.oxford import search_word
from exceptions import NoResultError
from views import PrintStyle

DICT_CSS_SELECTOR = {
    'oxford': 'div.box_wrap1.dicType_O',
    'donga': 'div.box_wrap1.dicType_D',
    'YBM': 'div.box_wrap1.dicType_U',
    'etc': 'div.box_wrap1_mar1',
}
URL = {
    'base': 'http://endic.naver.com',
    'ajax': 'http://endic.naver.com/ajax_enkrEntry.nhn',
}
DEFAULT_DICT = 'oxford'


def data_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        raise ConnectionError


def get_term_url(html, css_selector='dt.first > span > a'):
    bs = BeautifulSoup(html, 'html.parser')
    try:
        first_result = bs.select_one(css_selector)
        first_url = first_result.attrs['href']
        term = first_result.text
        return f'{URL["base"]}/{first_url}', term
    except:
        raise NoResultError


def request_term(first_result):
    try:
        return data_request(first_result)
    except:
        raise NoResultError


def get_dict_data(html, dict_type=DEFAULT_DICT, sentence=False):
    if sentence:
        dict_type = DEFAULT_DICT
    bs = BeautifulSoup(html, 'html.parser')
    results = bs.select(DICT_CSS_SELECTOR[dict_type])
    dict_selector = DICT_CSS_SELECTOR.copy()

    while not results:
        dict_selector.pop(dict_type)
        if not dict_selector:
            raise NoResultError
        dict_type = list(dict_selector.keys())[0]
        results = bs.select(dict_selector[dict_type])
    dict_meaning = ''

    for result in results:
        dict_meaning += ('*' + result.select_one('h3 > span.fnt_syn').text + '\n') \
            if result.select_one('h3 > span.fnt_syn') else ''
        for data in result.select('dl.list_a3 > *'):
            if str(data).startswith('<dt'):  # TODO: 이부분 더 좋은 방법으로 수정
                index = ''.join(s for s in data.select_one('span').text if s.isdigit())
                dict_meaning += ''.join([index, '.']) if index else '-' + ' '
                dict_meaning += ' '.join([item.text for item in data.select('em > span')])
                dict_meaning += '\n'
            elif sentence and dict_type == DEFAULT_DICT and str(data).startswith('<dd class="first'):
                dict_meaning += PrintStyle.GREEN + \
                                re.sub(r'(^\n\n)', '\tex) ', data.text).replace('\n\n', '\n\t    ') + \
                                PrintStyle.ENDC
        dict_meaning += '\n'
    return dict_meaning, dict_type


def renew_html(_url, _dict_type):
    _html = request_term(_url)
    bs = BeautifulSoup(_html, 'html.parser')
    css_id = f'#{DICT_CSS_SELECTOR[_dict_type].split(".")[-1]} > a'
    dict_tag = bs.select_one(css_id)
    if _dict_type != DEFAULT_DICT and dict_tag:
        _url = f'{URL["ajax"]}?entryId={dict_tag.attrs["entryid"]}'
        _html = data_request(_url)
    return _html


def search(term, refine_term=False):
    if refine_term:
        term = search_word(term)
    url = f'{URL["base"]}/search.nhn?sLn=kr&isOnlyViewEE=N&query={term}'
    return get_term_url(data_request(url))


def get_data(term, url=None, dict_type=DEFAULT_DICT):
    if not term:
        url, term = search(term)
    return {'html': renew_html(url, dict_type), 'term': term}
