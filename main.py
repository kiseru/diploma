from parse_kpfu import parse_kpfu
from parse_scholar_articles import parse_scholar_articles

EMPLOYERS_JSON = 'employers.json'
HTML_PARSER = 'html.parser'
JSON_INDENT = 2
LINKS = 'Ссылки'

if __name__ == '__main__':
    parse_kpfu()
    parse_scholar_articles()
