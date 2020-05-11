import json
from collections import Counter

import networkx as nx
from transliterate import translit

import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('employers.json', 'r', encoding='utf-8') as fp:
        employers = json.load(fp)

    employer_short_names = {}

    for employer, employer_info in employers.items():
        last_name, first_name, middle_name = employer.split(' ')
        employer_short_names[f'{first_name[0]}{middle_name[0]} {last_name}'] = employer
        employer_short_names[f'{first_name} {last_name}'] = employer
        employer_short_names[employer] = employer
        employer_short_names[f'{first_name} {middle_name} {last_name}'] = employer

        translit_employer = translit(employer, 'ru', reversed=True)
        last_name, first_name, middle_name = translit_employer.split(' ')
        employer_short_names[f'{first_name[0]}{middle_name[0]} {last_name}'] = employer
        employer_short_names[f'{first_name} {last_name}'] = employer
        employer_short_names[employer] = employer
        employer_short_names[f'{first_name} {middle_name} {last_name}'] = employer

    G = nx.Graph()

    for employer, employer_info in employers.items():
        counter = Counter()
        if 'co-authors' not in employer_info:
            continue

        for co_author, count in employer_info['co-authors'].items():
            if co_author not in employer_short_names:
                continue

            if employer_short_names[co_author] == employer:
                continue

            counter[employer_short_names[co_author]] += count

        print(dict(counter))
        for name in dict(counter).keys():
            G.add_edge(employer, name)

    plt.subplot(121)
    # nx.draw(G, with_labels=True, font_size=8)
    # plt.show()
