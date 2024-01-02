import os
import re
import glob
import logging

import cssutils
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

def convert_to_markdown(soup):
    markdown = MarkdownConverter().convert_soup(soup)
    return markdown

def extract_css_styles(soup):
    cssutils.log.setLevel(logging.CRITICAL)
    styles = soup.find_all('style')
    css_classes = {}
    for style in styles:
        css_sheet = cssutils.parseString(style.encode_contents())
        for rule in css_sheet:
            if rule.type == rule.STYLE_RULE:
                style = cssutils.css.CSSStyleDeclaration(cssText=rule.style.cssText)
                for property in ['font-weight', 'font-style', 'text-decoration']:
                    style_str = ''
                    if property == 'font-weight' and style[property] == '700':
                        style_str = 'bold'
                    if property == 'font-style' and style[property] == 'italic':
                        style_str = 'italic'
                    if property == 'text-decoration' and style[property] == 'underline':
                        style_str = 'underline'
                    if style_str:
                        if style_str in css_classes:
                            css_classes[style_str].add(rule.selectorText.replace('.', ''))
                        else:
                            css_classes[style_str] = set([rule.selectorText.replace('.', '')])
    if 'bold' not in css_classes:
        css_classes['bold'] = set()
    if 'italic' not in css_classes:
        css_classes['italic'] = set()
    return css_classes

def replace_newline(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s([,.;?!])', r'\1', text) # remove space before punctuation
    text = re.sub(r'\(\s*', '(', text) # remove space after opening parenthesis
    text = re.sub(r'\s*\)', ')', text) # remove space before opening parenthesis
    return text

def soup_to_wikidot(soup):
    css_classes = extract_css_styles(soup)
    soup = soup.body
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(header.name[1])
        header.replace_with('+' * level + ' ' + header.get_text().strip())

    for a in soup.find_all('a'):
        if not 'href' in a.attrs:
            continue
        url = a['href']
        text = a.get_text().strip()
        text = f'[[[{url} | {text}]]]'
        a.replace_with(text)

    for img in soup.find_all('img'):
        url = img['src']
        text = f'[[image {url}]]'
        img.replace_with(text)

    for span in soup.find_all('span'):
        text = span.get_text().strip()
        if not text:
            continue
        classes = set()
        if 'class' in span.attrs:
            classes = set(span['class'])
        if css_classes['bold'] & classes:
            text = '**' + text + '**'
        if css_classes['italic'] & classes:
            text = '//' + text + '//'
        span.replace_with(text)

    for ul in soup.find_all('ul'):
        text = ''
        for li in ul.find_all('li'):
            text += '* ' + replace_newline(li.get_text()) + '\n'
        ul.replace_with(text)

    for ol in soup.find_all('ol'):
        text = ''
        for li in ol.find_all('li'):
            text += '# ' + replace_newline(li.get_text()) + '\n'
        ol.replace_with(text)

    for p in soup.find_all('p'):
        text = p.get_text()
        text = replace_newline(text)
        text += '\n'
        p.replace_with(text)

    for hr in soup.find_all('hr'):
        hr.replace_with('----')

    for table in soup.find_all('table'):
        text = ''
        for tr in table.find_all('tr'):
            text += '||'
            for td in tr.find_all('td'):
                text += td.get_text().strip() + '||'
            text += '\n'
        table.replace_with(text)

    wikidot = soup.get_text()
    wikidot = re.sub(r'^\s*$', '', wikidot, flags=re.MULTILINE)
    wikidot = re.sub(r'\n\n\n*', '\n\n', wikidot)
    return wikidot

if __name__ == '__main__':
    with open('scenarios.tsv') as scenario_list_file:
        for line in scenario_list_file:
            fields = line.strip().split('\t')
            name = fields[0]
            title = fields[1]
            url = fields[2]
            teaser = fields[3]
            print(f'Converting {name}')
            html_path = f'scenarios/html/{name}.html'
            html = open(html_path).read()
            soup = BeautifulSoup(html, 'lxml')
            wikidot = soup_to_wikidot(soup)

            wikidot += f'\n++ Credits\n{title} was written by TBD for the 2023 Shotgun Scenario contest.\nSource: {url}'
            with open(f'scenarios/wikidot/{name}.md', 'w') as wikidot_file:
                wikidot_file.write(wikidot)

