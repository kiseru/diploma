import requests
from bs4 import BeautifulSoup
import json

kfu_employers_page_url = 'https://kpfu.ru/staff/sotrudniki-kfu'


def find_select_of_institutes():
    r = requests.get(kfu_employers_page_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.find('select', attrs={'name': 'p_id'})))


def get_employers():
    kfu_value_in_search_form = 0
    kfu_main_page_url = 'https://kpfu.ru/main_page'
    r = requests.post(kfu_main_page_url, data={'p_id': 6895, 'p_sub': 7860, 'p_order': 1})
    soup = BeautifulSoup(r.text, 'html.parser')

    employers_count = int(
        soup.select('#ss_content > div.area_width > div > div:nth-child(2) > table > tr > td')[0].string.split(' ')[1]
    )

    r = requests.post(
        kfu_main_page_url,
        data={'p_id': 6895, 'p_sub': 7860, 'p_order': 1, 'p_rec_count': employers_count}
    )
    soup = BeautifulSoup(r.text, 'html.parser')
    anchors = [i.find('a') for i in soup.find_all('tr', attrs={'class': 'konf_tr'})]
    anchors = {anchor['href']: anchor.string for anchor in anchors if anchor is not None}
    return anchors


def get_employer_info(employer_link, employer_name):
    soup = BeautifulSoup(requests.get(employer_link).text, 'html.parser')
    try:
        employer_info = soup.select('.left_width > div > div > div')[1].select('div')
    except IndexError:
        return {}
    data = {
        'link': employer_link,
    }
    lst = [(employer_info[i], employer_info[i + 1]) for i in range(0, len(employer_info), 2)]
    for (key, value) in lst:
        values = [i.get_text().replace('\n', '') for i in value.select('.menu_list > .li_spec')]
        data[key.get_text()] = values

    return employer_name, data


employers = get_employers()
result = [get_employer_info(employer_link, employer_name) for (employer_link, employer_name) in employers.items()]
result = [i for i in result if len(i) > 0]
with open('employers.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps({key: value for (key, value) in result}, ensure_ascii=False, sort_keys=True, indent=4))
