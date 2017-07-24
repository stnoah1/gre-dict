import os
import threading
from datetime import datetime

import settings
import views
from client import db, naver, oxford, quizlet
from exceptions import NoResultError
from views import PrintStyle


def search_db(term, options, update=True):
    db_data = db.search(name=term)
    if db_data.empty:
        return {}
    options.append('DELETE')
    db_data = db_data.iloc[0].to_dict()
    search_count = db_data["count"] if db_data['recent_search'] == datetime.today().strftime('%Y-%m-%d') \
        else db_data["count"] + 1
    if update:
        threading.Thread(target=db.update, args=(db_data['id'],)).start()
    options.append('EXAMPLE')
    main_text = {
        'term': term,
        'search_count': search_count,
        'dict_type': db_data['source'],
        'definition': db_data['meaning'],
        'history': f'search_count: {search_count}회, recent_search: {db_data["recent_search"]}\n'
    }

    return {'main_text': main_text, 'options': options, 'meta': {'source': 'db'}}


def search_naver(term, dict_type, options, url=None):
    naver_data = naver.get_data(term, url=url, dict_type=dict_type)
    definition, dict_type, example = naver.get_dict_data(naver_data['html'], dict_type)
    options.append('PASS')
    if example:
        options.append('EXAMPLE')
    main_text = {
        'term': naver_data['term'],
        'history': '',
        'search_count': 1,
        'dict_type': dict_type,
        'definition': definition,
    }
    return {'main_text': main_text, 'options': options, 'meta': {'source': 'naver', 'html': naver_data['html']}}


def main(search_log=None, term=None):
    os.system("clear")
    if search_log is None:
        search_log = []
    if not term:
        term = views.input_term()
        update_db = True
        options = ['ENTER']
    else:
        update_db = False
        options = ['PASS']
    options.append('ENDIC')
    url, term = naver.search(term)
    dict_type = settings.NAVER_DICT_TYPE

    if search_log:
        options = ['BACK'] + options

    data = search_db(term, options, update=update_db)
    if not data:
        data = search_naver(term, dict_type, options, url=url)

    term = data['main_text']['term']
    definition = data['main_text']['definition']
    dict_type = data['main_text']['dict_type']
    view_data = data['main_text'].copy()
    options = data['options'].copy()
    meta_data = data['meta']
    view_data.update({
        'relevant_data': ''.join(db.search_dictionary(dictionary, term) for dictionary in ['거만어', '박정'])
    })

    # main view
    views.main(**view_data)

    # option selection
    while True:
        options = list(set(options))
        selected = views.select_option(options)

        if selected == 'PASS':
            break

        elif selected == 'ENTER':
            if meta_data['source'] == 'naver':
                threading.Thread(target=db.insert, args=(term, definition, dict_type,)).start()
            threading.Thread(target=quizlet.send_voca, args=(term, definition,)).start()
            break

        elif selected == 'DELETE':
            threading.Thread(target=db.delete, kwargs={'name': term}).start()
            break

        elif selected == 'BACK':
            return main(term=search_log[-1], search_log=search_log[:-1])

        elif selected == 'ENDIC':
            os.system("clear")
            print(f"WORD: {PrintStyle.BOLD}{term}{PrintStyle.ENDC}", end='\r')
            print(oxford.search(term, num_sentence=2))
            options = ['KODIC' if option == 'ENDIC' else option for option in options]
            if 'EXAMPLE' in options:
                options.remove('EXAMPLE')
            views.show_option(options)

        elif selected == 'KODIC':
            views.main(**view_data)
            options = data['options'].copy()
            views.show_option(options)

        elif selected == 'EXAMPLE':
            if meta_data['source'] == 'naver':
                html = meta_data['html']
            else:
                html = naver.get_data(term, url=url, dict_type=dict_type)['html']

            print_text, _, _ = naver.get_dict_data(html, sentence=True)
            view_data['definition'] = print_text
            views.main(**view_data)
            options.remove('EXAMPLE')
            views.show_option(options)
    return term


if __name__ == '__main__':
    log = []
    while True:
        try:
            search_result = main(search_log=log)
            log.append(search_result)
        except NoResultError:
            input()
        except BaseException as e:
            views.exception(e)
            input()
        except ConnectionError as e:
            views.exception(e)
            input()
