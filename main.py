import requests
from bs4 import BeautifulSoup
import json

kfu_employers_page_url = 'https://kpfu.ru/staff/sotrudniki-kfu'


def find_select_of_institutes():
    r = requests.get(kfu_employers_page_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.find('select', attrs={'name': 'p_id'})))


kfu_value_in_search_form = 0
kfu_main_page_url = 'https://kpfu.ru/main_page'
r = requests.post(kfu_main_page_url, data={'p_id': 6895, 'p_sub': 7860, 'p_order': 1})
soup = BeautifulSoup(r.text, 'html.parser')

#ss_content > div.area_width > div > div:nth-child(2) > table:nth-child(5) > tbody > tr > td
employers_count = int(soup.select('#ss_content > div.area_width > div > div:nth-child(2) > table > tr > td')[0].string.split(' ')[1])

r = requests.post(kfu_main_page_url, data={'p_id': 6895, 'p_sub': 7860, 'p_order': 1, 'p_rec_count': employers_count})
soup = BeautifulSoup(r.text, 'html.parser')
with open('anchors.json', 'w') as f:
    anchors = [i.find('a') for i in soup.find_all('tr', attrs={'class': 'konf_tr'})]
    anchors = {anchor['href']: anchor.string for anchor in anchors if anchor is not None}
    print(anchors)
    f.write(json.dumps(anchors, sort_keys=True, indent=4))
