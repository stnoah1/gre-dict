import datetime
import os

import requests
from bs4 import BeautifulSoup


def get_class_announce(announce_type, css_selector='div.rd_body.clear',
                       save_folder='/Users/noah/Documents/유학/GRE/박정/공지'):

    today = datetime.datetime.today()
    site_url = 'http://koreagre.com/index.php'
    file_name = f"{today.strftime('%Y%m%d')}_{announce_type}.html"
    file_path = os.path.join(save_folder, file_name)

    if announce_type == '기본':
        mid = 'weekdaybasic'
        document_srl = '340'
    elif announce_type == '실전':
        mid = 'mwfactual'
        document_srl = '10495'
    else:
        raise IOError

    url = f'{site_url}?mid={mid}&document_srl={document_srl}'
    r = requests.get(url).text
    bs = BeautifulSoup(r, 'html.parser')
    html_data = bs.select_one(css_selector)
    with open(file_path, 'w') as f:
        f.write(str(html_data))


if __name__ == '__main__':
    get_class_announce('기본')
    get_class_announce('실전')
