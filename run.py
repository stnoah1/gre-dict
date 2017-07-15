import os
import threading
from datetime import datetime

import settings
import views
from client import db, naver
from client.oxford import WrongWordError
from client.quizlet import send_voca
from exceptions import NoResultError


def search_db(voca, options):
    db_data = db.search(name=voca)
    if db_data.empty:
        return {}
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
        'dict_meaning': db_data['meaning'],
        'history': f'search_count: {search_count}회, recent_search: {db_data["recent_search"]}\n',
        'etc': {'source': 'db'},
    }


def search_naver(voca, dict_type, options, url=None):
    naver_data = naver.get_data(voca, url=url, dict_type=dict_type)
    dict_meaning, dict_type = naver.get_dict_data(naver_data['html'], dict_type)
    threading.Thread(target=db.insert, args=(voca, dict_meaning, dict_type,)).start()
    options.append('PASS')
    if dict_type == naver.DEFAULT_DICT:
        options.append('EXAMPLE')
    return {
        'voca': naver_data['voca'],
        'history': '',
        'search_count': 1,
        'dict_type': dict_type,
        'options': options,
        'dict_meaning': dict_meaning,
        'etc': {'source': 'naver', 'html': naver_data['html']},
    }


def main(search_log=None, voca=None):
    os.system("clear")
    if search_log is None:
        search_log = []
    if not voca:
        voca = views.input_voca()

    url, voca = naver.search(voca)
    dict_type = settings.NAVER_DICT_TYPE
    options = []

    if search_log:
        options.append('BACK')

    search_data = search_db(voca, options)
    if not search_data:
        search_data = search_naver(voca, dict_type, options, url=url)
    relevant_data = ''.join(db.search_dictionary(dictionary, search_data['voca']) for dictionary in ['거만어', '박정'])
    search_data.update({'relevant_data': relevant_data})
    voca = search_data['voca']
    view_data = search_data.copy()
    view_data.pop('etc')
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
                if search_data['etc']['source'] == 'naver':
                    html = search_data['etc']['html']
                else:
                    html = naver.get_data(voca, url=url, dict_type=dict_type)['html']
                print_text, _ = naver.get_dict_data(html, sentence=True)
                search_data['dict_meaning'] = print_text
                search_data['options'].remove(select_option)
                view_data = search_data.copy()
                view_data.pop('etc')
                views.main(**view_data)
            if select_option == 'BACK':
                return main(voca=search_log[-1], search_log=search_log[:-1])
        else:
            views.wrong_option(select_option)
    return voca


if __name__ == '__main__':
    log = []
    while True:
        try:
            log.append(main(search_log=log))
        except WrongWordError:
            views.no_result()
            input()
        except NoResultError:
            input()
        except BaseException as e:
            views.exception(e)
            input()
        except ConnectionError as e:
            views.exception(e)
            input()
