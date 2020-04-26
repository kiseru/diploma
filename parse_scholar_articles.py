import json

import requests
from bs4 import BeautifulSoup

GOOGLE_SCHOLAR = 'Google scholar'
HTTPS_SCHOLAR_GOOGLE_RU = 'https://scholar.google.ru'
EMPLOYERS_JSON = 'employers.json'
HTML_PARSER = 'html.parser'
JSON_INDENT = 2
LINKS = 'Ссылки'


def parse_scholar_articles():
    with open(EMPLOYERS_JSON, 'r', encoding='utf-8') as fp:
        employers = json.load(fp)

    employers_with_scholar_names = [
        employer
        for employer, employer_info in employers.items()
        if GOOGLE_SCHOLAR in employer_info[LINKS]
    ]

    for employer in employers_with_scholar_names:
        employer_scholar_link = employers[employer][LINKS][GOOGLE_SCHOLAR]
        scholar_response = requests.get(employer_scholar_link)
        bs = BeautifulSoup(scholar_response.text, HTML_PARSER)
        bs_articles = bs.select("#gsc_a_t .gsc_a_tr")
        articles = [parse_article(bs_article) for bs_article in
                    bs_articles]
        co_authors = list({co_author for article in articles
                      for co_author in article['authors']})
        employers[employer][GOOGLE_SCHOLAR] = articles
        employers[employer]['co-authors'] = co_authors
        with open(EMPLOYERS_JSON, 'w', encoding='utf-8') as fp:
            json.dump(employers, fp, ensure_ascii=False, indent=JSON_INDENT)


def parse_article(bs_article):
    try:
        bs_article_title = bs_article.select_one('.gsc_a_t a')
        bs_article_cited_by = bs_article.select_one('.gsc_a_c a')
        bs_article_year = bs_article.select_one('.gsc_a_y span')
        return {
            'title': str(bs_article_title.string),
            'link': HTTPS_SCHOLAR_GOOGLE_RU + bs_article_title['data-href'],
            'cited_by': int(bs_article_cited_by.string)
            if bs_article_cited_by.string is not None else 0,
            'year': int(bs_article_year.string)
            if bs_article_year.string is not None else -1,
            'authors': parse_authors(bs_article_title),
        }
    except AttributeError as e:
        print(e)


def parse_authors(bs_article):
    link = bs_article['data-href']
    article = requests.get(f'{HTTPS_SCHOLAR_GOOGLE_RU}{link}')
    bs_article = BeautifulSoup(article.text, HTML_PARSER)
    bs_authors = bs_article.select_one('.gsc_vcd_value')
    return bs_authors.string.split(', ')
