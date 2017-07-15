import os
import threading
from datetime import datetime

import settings
import views
from client import db, naver
from client.quizlet import send_voca
from exceptions import NoResultError
from oxford import WrongWordError


def search_db(voca, options):
    db_data = db.search(name=voca)
    if db_data.empty:
        return None
    db_data = db_data.iloc[0].to_dict()
    search_count = db_data["count"] if db_data['recent_search'] == datetime.today().strftime('%Y-%m-%d') \
        else db_data["count"] + 1
    threading.Thread(target=db.update, args=(db_data['id'],)).start()
    options.append('EXAMPLE')
    return {
        'voca': voca,
        'options': options,
        'search_count': search_count,
        'dict_type': db_data['source'],
        'print_text': db_data['meaning'],
        'dict_meaning': db_data['meaning'],
        'history': f'search_count: {search_count}회, recent_search: {db_data["recent_search"]}\n',
    }


def search_naver(voca, dict_type, options, url=None):
    naver_data = naver.get_data(voca, url=url, dict_type=dict_type)
    dict_meaning, dict_type = naver.get_dict_data(naver_data['html'], dict_type)
    if dict_type == 'oxford':
        print_text, _ = naver.get_dict_data(naver_data['html'], sentence=True)
    else:
        print_text = dict_meaning
    threading.Thread(target=db.insert, args=(voca, dict_meaning, dict_type,)).start()
    options.append('PASS')
    return {
        'voca': naver_data['voca'],
        'history': '',
        'search_count': 1,
        'dict_type': dict_type,
        'print_text': print_text,
        'options': options,
        'dict_meaning': dict_meaning,
    }


def main():
    voca = views.input_voca()
    dict_type = settings.NAVER_DICT_TYPE

    url, voca = naver.search(voca)
    options = []

    search_data = search_db(voca, options)
    if not search_data:
        search_data = search_naver(voca, dict_type, options, url=url)
    relevant_data = ''.join(db.search_dictionary(dictionary, search_data['voca']) for dictionary in ['거만어', '박정'])
    search_data.update({'relevant_data': relevant_data})

    voca = search_data['voca']
    view_data = search_data.copy()
    view_data.pop('dict_meaning')
    views.main(**view_data)

    while True:
        select_option = input().upper()
        if not select_option:
            threading.Thread(target=send_voca, args=(search_data['voca'], search_data['dict_meaning'],)).start()
            break
        elif select_option in search_data['options']:
            if select_option == 'PASS':
                threading.Thread(target=db.delete, kwargs={'name': voca}).start()
                views.delete_option(voca)
                break
            if select_option == 'EXAMPLE':
                naver_data = naver.get_data(voca, url=url, dict_type=dict_type)
                print_text, _ = naver.get_dict_data(naver_data['html'], sentence=True)
                search_data['print_text'] = print_text
                search_data['options'].remove(select_option)
                view_data = search_data.copy()
                view_data.pop('dict_meaning')
                views.main(**view_data)
        else:
            views.wrong_option(select_option)


if __name__ == '__main__':
    while True:
        os.system("clear")
        # try:
        main()
        # except WrongWordError:
        #     views.no_result()
        #     input()
        # except NoResultError:
        #     input()
        # except BaseException as e:
        #     views.exception(e)
        #     input()
        # except ConnectionError as e:
        #     views.exception(e)
        #     input()
