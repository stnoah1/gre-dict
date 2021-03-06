# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import textwrap

import requests

from exceptions import NoResultError
from views import PrintStyle

APP_ID = 'e43d4320'
APP_KEY = '695f70fc2932507841ebc18cdf41f71e'
API_URL = 'https://od-api.oxforddictionaries.com/api/v1'
PREFERRED_WIDTH = 110


def get_oxford_dict_data(word_id, search_type='', region=''):
    if search_type:
        search_type = '/' + search_type
    if region:
        region = '/regions=' + region
    url = f'{API_URL}/entries/en/{word_id.lower()}{search_type}{region}'
    r = requests.get(url, headers={'app_id': APP_ID, 'app_key': APP_KEY})

    if r.status_code == 200:
        return r.json()['results']
    else:
        raise NoResultError


def search_word(word_id):
    url = f'{API_URL}/search/en?q={word_id.lower()}&prefix=false'
    r = requests.get(url, headers={'app_id': APP_ID, 'app_key': APP_KEY})
    if r.status_code == 200:
        return r.json()['results'][0]['word']
    else:
        raise NoResultError


def get_sentences(voca, word_id):
    sentences = []
    for result in get_oxford_dict_data(voca, search_type='sentences'):
        for lexicalEntry in result['lexicalEntries']:
            for sentence in lexicalEntry['sentences']:
                if word_id in sentence['senseIds']:
                    sentences.append(sentence['text'])
    return sentences


def get_synonyms(voca):
    synonyms = []
    for result in get_oxford_dict_data(voca, search_type='synonyms'):
        for lexicalEntry in result['lexicalEntries']:
            for entry in lexicalEntry['entries']:
                for sense in entry['senses']:
                    if sense.get('synonyms'):
                        synonyms.append([synonym['text'] for synonym in sense['synonyms']])
    return synonyms


def search(voca, num_sentence=0, synonyms=False, refine=False):
    # TODO: view 로 리펙토링하기, 비동기 request 사용해서 속도 개선해보기
    print_text = ''
    etymology_wrapper = textwrap.TextWrapper(initial_indent='\nEtymology : ',
                                             width=PREFERRED_WIDTH,
                                             subsequent_indent=' ' * (len('Etymology : ')))
    sentences_wrapper = textwrap.TextWrapper(initial_indent='\n' + ' ' * len('\tExample : ') + '- ',
                                             width=PREFERRED_WIDTH,
                                             subsequent_indent=' ' * (len('\tExample : ') + 2))
    definition_wrapper = textwrap.TextWrapper(initial_indent='\n  ',
                                              width=PREFERRED_WIDTH,
                                              subsequent_indent=' ' * 5)

    if refine:
        voca = search_word(voca)
    print_text += f'WORD: {PrintStyle.BOLD}{voca}{PrintStyle.ENDC}' + '\n'
    for result in get_oxford_dict_data(voca, region='us'):
        for lexicalEntries in result['lexicalEntries']:
            print_text += '\n\n*' + lexicalEntries['lexicalCategory'].upper()
            num_definition = 0
            for entry in lexicalEntries['entries']:
                # 어원
                for etymology in [] if entry.get('etymologies') is None else entry['etymologies']:
                    print_text += etymology_wrapper.fill(etymology)
                # 의미
                for index, sense in enumerate(entry['senses']):
                    if sense.get('definitions'):
                        for definition in sense['definitions']:
                            num_definition += 1
                            print_text += definition_wrapper.fill(f'{num_definition}. {definition}')
                        if num_sentence > 0:
                            print_text += '\n\tExample : '
                            sentences = get_sentences(voca, sense['id'])
                            for index in range(min(len(sentences), num_sentence)):
                                print_text += sentences_wrapper.fill(sentences[index])
    if synonyms:
        synonyms = get_synonyms(voca)
        print_text += '\t\tSynonyms : ', synonyms
    return print_text
