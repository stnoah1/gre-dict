from bs4 import BeautifulSoup

from client import naver


def search(word, line_sep=' '):
    html = naver.data_request(
        f'https://www.google.co.kr/async/dictw?async=term:{word},corpus:en-US,ttl:ko,tsl:en',
        return_type='json')
    bs = BeautifulSoup(html[1][1], 'html.parser')
    # div.vk_txt 영어 예문과 사전이 포함되어 있음
    word_types = [item.text for item in bs.select('.lr_dct_tg_pos.vk_txt') if item.text]
    word_definitions = [item.text for item in bs.select('li.vk_txt')]

    shortcut_item = []
    for word_definition in word_definitions:
        if ('1' in word_definition) and word_types:
            shortcut_item.append(f'*{word_types.pop(0)}')
        shortcut_item.append(word_definition)
    return line_sep.join(shortcut_item)