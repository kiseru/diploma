import requests
from bs4 import BeautifulSoup, Tag
import json

HTML_PARSER = 'html.parser'
KFU_MAIN_PAGE_URL = 'https://kpfu.ru/main_page'
KFU_EMPLOYERS_PAGE_URL = 'https://kpfu.ru/staff/sotrudniki-kfu'


def find_select_of_institutes():
    r = requests.get(KFU_EMPLOYERS_PAGE_URL)
    soup = BeautifulSoup(r.text, HTML_PARSER)

    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.find('select', attrs={'name': 'p_id'})))


def get_employers():
    r = requests.post(
        KFU_MAIN_PAGE_URL,
        data={'p_id': 6895, 'p_sub': 7860, 'p_order': 1},
    )
    soup = BeautifulSoup(r.text, HTML_PARSER)

    str_count = soup.select(
        '#ss_content > div.area_width > div > div:nth-child(2) > table > tr > td'  # noqa
    )[0].string.split(' ')[1]

    getting_employers_request_settings = {
        'p_id': 6895,
        'p_sub': 7860,
        'p_order': 1,
        'p_rec_count': int(str_count),
    }
    r = requests.post(
        KFU_MAIN_PAGE_URL,
        data=getting_employers_request_settings,
    )
    soup = BeautifulSoup(r.text, HTML_PARSER)
    anchors = [i.find('a') for i in
               soup.find_all('tr', attrs={'class': 'konf_tr'})]
    anchors = {
        anchor['href']: anchor.string for anchor in anchors if
        anchor is not None
    }
    return anchors


def get_employer_info(employer_link, employer_name):
    soup = BeautifulSoup(requests.get(employer_link).text, HTML_PARSER)
    data = {
        'link': employer_link,
    }

    try:
        info = soup.select(
            '.left_width > div > div > div',
        )[1]
        basic_info = info.select('div')

        data = {**data, **get_links(soup)}

        additional_info_header = info.find('b')
        if additional_info_header is not None:
            additional_info = additional_info_header.next_sibling.next_sibling
            data['Дополнительные сведения'] = parse_html_list(additional_info)
    except IndexError:
        return {}

    lst = [
        (basic_info[i], basic_info[i + 1])
        for i in range(0, len(basic_info), 2)
    ]
    for (k, v) in lst:
        values = [
            i.get_text().replace('\n', '') for i in
            v.select('.menu_list > .li_spec')
        ]
        data[k.get_text()] = values

    return employer_name, data


def parse_html_list(html_list):
    result = {
        'title': '',
        'items': [],
    }
    for item in html_list.contents:
        if item.name != 'li':
            continue

        if item.ul:
            title = [parse_html(i) for i in item.children
                     if i != '\n' and i.name != 'ul']

            result['items'].append(
                {**parse_html_list(item.ul), 'title': ' '.join(title)}
            )
            continue

        result['items'].append({'title': parse_html(item)})

    return result


def parse_html(html):
    if isinstance(html, Tag):
        return ' '.join(parse_html(item) for item in html.children)

    return str(html.string).strip()


def get_links(employer_soup):
    link_rows = employer_soup.select('.right_block > div:first-child table tr')
    links = {row.contents[0].string.strip()[:-1]: row.contents[1].string
             for row in link_rows}
    return {'Ссылки': links}


if __name__ == '__main__':
    employers = get_employers()
    result = [
        get_employer_info(link, name) for (link, name) in employers.items()
    ]
    result = [i for i in result if len(i) > 0]
    with open('employers.json', 'w', encoding='utf-8') as f:
        json_encoded = json.dumps(
            {key: value for (key, value) in result},
            ensure_ascii=False,
            sort_keys=True,
            indent=4,
        )
        f.write(json_encoded)
