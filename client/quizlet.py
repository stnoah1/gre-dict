import base64
from datetime import datetime

import requests

API_INFO = {
    'public_id': 'sU7xZkMMzt',
    'secret_key': 'bxZQYJGXAUfZjhDnpjmSAD',
    'id': 'stnoah1',
}
URL = {
    'base': 'https://quizlet.com',
    'api': 'https://api.quizlet.com',
    'auth': 'https://quizlet.com/authorize',
}
ACCESS_TOKEN = 'ggsFNy54szFtrawF6Qyfvg9vpe8JY25EapwnvfZH'  # expires_in 315360000s
API_INFO_BASE64 = str(base64.b64encode(bytes((API_INFO["public_id"] + ':' + API_INFO["secret_key"]), "utf-8")), "utf-8")
# TODO: 고치기


def get_data(user_id=API_INFO['id']):
    url = f'{URL["api"]}/2.0/users/{user_id}/sets?client_id={API_INFO["public_id"]}'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise ConnectionError


def post_data():
    url = F'{URL["api"]}/2.0/sets'
    header = {
        'Authorization': f'Bearer {API_INFO_BASE64}',
    }
    data = {
        'title': ' real_test,',
    }
    r = requests.post(url, headers=header, data=data)
    if r.status_code == 200:
        return r.json()
    else:
        raise ConnectionError


def authorization_step_1():
    return requests.get(
        f'{URL["auth"]}?response_type=code&client_id={API_INFO["public_id"]}&scope=read write_set&state=RANDOM_STRING')


def authorization_step_2(generated_code):
    url = f'{URL["api"]}/oauth/token?grant_type=authorization_code&code={generated_code}'
    header = {
        'Host': 'api.quizlet.com',
        'Client id': API_INFO["public_id"],
        'Authorization': f'Basic {API_INFO_BASE64}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'charset': 'UTF-8',
    }
    return requests.post(url, headers=header)


def create_set(title, data):
    url = f'{URL["api"]}/2.0/sets'
    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    # append dummy in case of data size 1 because sets must have at least 2 terms
    if len(data['terms']) == 1 or len(data['definitions']) == 1:
        dummy_term = ['term']
        dummy_definition = ['definition']
        data['terms'] = dummy_term + data['terms']
        data['definitions'] = dummy_definition + data['definitions']
    payload = {
        'title': title,
        'terms': data['terms'],
        'definitions': data['definitions'],
        'lang_terms': 'en',
        'lang_definitions': 'ko',
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 201:
        return True
    else:
        return r.json()


def add_term(set_id, data):
    url = f'{URL["api"]}/2.0/sets/{set_id}/terms'
    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }
    payload = {
        'term': data['terms'],
        'definition': data['definitions'],
    }
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 201:
        return True
    else:
        return r.json()


def delete_term(set_id, term_id):
    url = f'{URL["api"]}/2.0/sets/{set_id}/terms/{term_id}'
    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }
    r = requests.delete(url, headers=headers)
    if r.status_code == 201:
        return True
    else:
        return r.json()


def add_to_quizlet(term, definition):
    data = {'terms': [term], 'definitions': [definition]}
    set_title = datetime.today().strftime('gre-%Y-%m-%d')
    set_id = None
    for item in get_data():
        if item['title'] == set_title:
            if term not in [voca_data['term'] for voca_data in item['terms']]:
                set_id = item['id']
                add_term(set_id, data=data)
            return
    if not set_id:
        create_set(set_title, data=data)


def get_data_from_quizlet(user_id, table_name):
    """
    박정 - user_id:'naeun_kim5', table_name :'gre_dictionary_1'
    거만어 - user_id: {'ilj0411', 'nintyning'}, table_name :'gre_dictionary_2'
    """
    import pandas as pd
    from client.db import CONN

    data_table = pd.DataFrame(columns=['name', 'meaning', 'day'])
    name = []
    meaning = []
    index = []
    raw_data = get_data(user_id)
    for day_data in raw_data:
        if day_data['title'].startswith('거만어 Day'):
            for term_info in day_data['terms']:
                name.append(term_info['term'].lower())
                meaning.append(term_info['definition'])
                index.append(''.join([s for s in day_data['title'] if s.isdigit()]))
    data_table['name'] = name
    data_table['meaning'] = meaning
    data_table['day'] = index
    data_table.to_sql(name=table_name, con=CONN, if_exists='append', index=False)


def make_test(start_day, end_day, num_term=25):
    import pandas as pd
    from client.db import CONN

    return print(pd.read_sql_query(
        f"""select name, meaning
        from gre_dictionary
        where day BETWEEN {start_day}
        and {end_day}
        order by random()
        limit {num_term}""",
        CONN,
    ).to_csv(sep='\t', index=False))