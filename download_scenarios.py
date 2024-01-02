import re

import requests
from bs4 import BeautifulSoup

def download_google_doc_html(url):
    doc_id = url.split('/d/')[1].split('/')[0]
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(export_url)
    if response.status_code == 200:
        return str(response.text)
    print(f'Failed to download scenario from {url}')

def get_scenarios(html):
    scenarios = []
    soup = BeautifulSoup(html, 'lxml')
    scenario_list = soup.html.body.ol
    for list_item in scenario_list.find_all('li'):
        spans = list_item.find_all('span')
        link_span = spans[0]
        teaser_span = spans[-1]
        link = link_span.find('a')
        title = link.text
        url = link['href']
        teaser = teaser_span.text.strip()
        if ' - ' in teaser:
            teaser = teaser.split(' - ')[1].strip()
        scenario = (title, url, teaser)
        scenarios.append(scenario)
    return scenarios

if __name__ == '__main__':
    contest_doc_url = 'https://docs.google.com/document/d/1yLsMjxHVLNgw63phSgnsEkx_UJa7R5dBjT3hXb_dK_0/edit'

    contest_doc_html = download_google_doc_html(contest_doc_url)

    scenarios = get_scenarios(contest_doc_html)

    name_pattern = re.compile('[\W]+')
    with open('scenarios.tsv', 'w') as tsv_file:
        for title, url, teaser in scenarios:
            name = title.lower().replace(' ', '_')
            name = name_pattern.sub('', name)
            print(f'Downloading scenario {name}')
            scenario_html = download_google_doc_html(url)
            scenario_html = BeautifulSoup(scenario_html, 'lxml').prettify()
            with open(f'scenarios/html/{name}.html', 'w') as scenario_file:
                scenario_file.write(scenario_html)
            line = f'{name}\t{title}\t{url}\t{teaser}\n'
            tsv_file.write(line)

