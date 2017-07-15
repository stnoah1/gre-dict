import os
import threading
from datetime import datetime

import settings
import views
from client import db, naver
from client.quizlet import send_voca
from exceptions import NoResultError
from oxford import WrongWordError


def run_option(option):
    while True:
        select_option = input().upper()
        if not select_option:
            return 'send_voca'
        elif select_option in option:
            if select_option == 'PASS':
                return 'delete_voca'
        else:
            views.wrong_option(select_option)


def main(dict_type):
    voca = views.input_voca()

    first_url, voca = naver.search(voca)
    db_data = db.search(name=voca)
    search_count = 1
    history = ''
    option_list = []

    if db_data.empty:
        html = naver.renew_html(first_url, dict_type)
        dict_meaning, dict_type = naver.get_dict_data(html, dict_type)
        print_text, _ = naver.get_dict_data(html, dict_type, sentence=True)
        threading.Thread(target=db.insert, args=(voca, dict_meaning, dict_type,)).start()
        option_list.append('PASS')
    else:
        db_data = db_data.iloc[0].to_dict()
        dict_meaning = db_data['meaning']
        dict_type = db_data['source']
        search_count = db_data["count"] if db_data['recent_search'] == datetime.today().strftime('%Y-%m-%d') \
            else db_data["count"] + 1
        history = f'search_count: {search_count}회, recent_search: {db_data["recent_search"]}\n'
        threading.Thread(target=db.update, args=(db_data['id'],)).start()
        print_text = dict_meaning

    relevant_data = ''.join(db.search_dictionary(dictionary, voca) for dictionary in ['거만어', '박정'])
    views.main(voca, dict_type, search_count, print_text, history, relevant_data, option_list)

    command = run_option(option_list)
    if command == 'send_voca':
        threading.Thread(target=send_voca, args=(voca, dict_meaning,)).start()
    elif command == 'delete_voca':
        threading.Thread(target=db.delete, kwargs={'name': voca}).start()
        views.delete_option(voca)


if __name__ == '__main__':
    while True:
        os.system("clear")
        try:
            main(settings.NAVER_DICT_TYPE)
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
