from pprint import pprint

import requests


class Error404(BaseException):
    pass


# https://newsapi.org/
def search_news(source='time', sort='top'):
    api_url = 'https://newsapi.org/v1/articles'
    api_key = 'c8674d227d844dc281fc9b8ed4cc7c7b'
    url = f'{api_url}?source={source}&sortBy={sort}&apiKey={api_key}'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise Error404


# https://developer.nytimes.com/
def get_NYT_articles(word):
    api_key = 'c5ab6291f70b4a818a1913827f873dac'
    api_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?api_key={api_key}&q={word}"
    r = requests.get(api_url)
    if r.status_code == 200:
        return r.json()
    else:
        raise Error404


pprint(search_news())
