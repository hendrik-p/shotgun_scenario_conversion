import argparse
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

def download_scenario(url, out_path):
    scenario_html = download_google_doc_html(url)
    with open(out_path, 'w') as scenario_file:
        scenario_file.write(scenario_html)

def parse_contest_doc(html):
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
        url = url.split('?q=')[1].split('?')[0]
        author = 'TBD'
        teaser = teaser_span.text.strip()
        if ' - ' in teaser:
            splitted = teaser.split(' - ')
            author_match = re.match('(by )?(.*)', splitted[0])
            author = author_match.group(2)
            teaser = splitted[1]
        scenario = (title, url, author, teaser)
        scenarios.append(scenario)
    return scenarios

def get_scenario_list_from_contest_doc(contest_doc_url):
    contest_doc_html = download_google_doc_html(contest_doc_url)
    scenarios = parse_contest_doc(contest_doc_html)
    return scenarios

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contest-doc')
    parser.add_argument('--scenario')
    parser.add_argument('--output-path')
    parser.add_argument('--scenario-tsv-path')
    args = parser.parse_args()

    if args.contest_doc:
        scenarios = get_scenario_list_from_contest_doc(args.contest_doc)
        name_pattern = re.compile('[\W]+')
        scenario_tsv_path = 'scenarios.tsv'
        if args.scenario_tsv_path:
            scenario_tsv_path = args.scenario_tsv_path
        with open(scenario_tsv_path, 'w') as tsv_file:
            for title, url, author, teaser in scenarios:
                name = title.lower().replace(' ', '_')
                name = name_pattern.sub('', name)
                print(f'Downloading scenario {name}')
                download_scenario(url, f'{args.output_path}/{name}.html')
                line = f'{name}\t{title}\t{url}\t{author}\t{teaser}\n'
                tsv_file.write(line)
    elif args.scenario:
        download_scenario(args.scenario, args.output_path)

