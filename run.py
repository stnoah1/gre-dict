import os
from datetime import datetime

import settings
import views
from client import db, naver
from client.quizlet import add_to_quizlet
from exceptions import NoResultError
from oxford import WrongWordError


def main(voca, dict_type):
    first_url, voca = naver.search(voca)
    db_data = db.search(name=voca)
    search_count = 1
    history = ''

    if db_data.empty:
        html = naver.renew_html(first_url, dict_type)
        dict_meaning, dict_type = naver.get_dict_data(html, dict_type)
        print_text, _ = naver.get_dict_data(html, dict_type, sentence=True)
        db.save(voca, dict_meaning, dict_type)
    else:
        db_data = db_data.iloc[0].to_dict()
        dict_meaning = db_data['meaning']
        dict_type = db_data['source']
        search_count = db_data["count"] if db_data['recent_search'] == datetime.today().strftime('%Y-%m-%d') \
            else db_data["count"] + 1
        history = f'\nsearch_count: {search_count}회, recent_search: {db_data["recent_search"]}'
        db.update(db_data['id'])
        print_text = dict_meaning

    relevant_data = '\n'.join(db.search_dictionary(dictionary, voca) for dictionary in ['거만어', '박정'])
    views.main(voca, dict_type, search_count, print_text, history, relevant_data)
    add_to_quizlet(voca, dict_type)


if __name__ == '__main__':
    os.system("clear")
    vocabulary = input("ENTER WORD: ")
    while True:
        try:
            main(vocabulary, settings.NAVER_DICT_TYPE)
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
