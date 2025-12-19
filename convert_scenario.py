import os
import re
import base64
import argparse
import logging

import cssutils
from bs4 import BeautifulSoup

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
    text = text.strip()
    return text

def highlight_text(text, markup):
    stripped_text = text.strip()
    leading_spaces = text[:len(text) - len(text.lstrip())]
    trailing_spaces = text[len(text.rstrip()):]
    out = f'{leading_spaces}{markup}{stripped_text}{markup}{trailing_spaces}'
    return out

def soup_to_wikidot(soup, img_prefix=''):
    css_classes = extract_css_styles(soup)
    soup = soup.body

    # handle headers
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(header.name[1])
        header.replace_with('+' * (level + 1) + ' ' + header.get_text().strip() + '\n')

    # handle links
    for a in soup.find_all('a'):
        if not 'href' in a.attrs:
            continue
        url = a['href']
        text = a.get_text().strip()
        text = f'[[[{url} | {text}]]]'
        a.replace_with(text)

    # handle images
    images = []
    for i, img in enumerate(soup.find_all('img')):
        text = ''
        if 'src' in img.attrs:
            url = img['src']
            if url.startswith('data'):
                _, encoded = url.split(',', 1)
                img_data = base64.b64decode(encoded)
                img_name = f'{img_prefix}_{i}.png'
                images.append((img_name, img_data))
                url = img_name
            text = f'[[image {url} size="medium"]]'
        img.replace_with(text)

    # handle stylized text
    for span in soup.find_all('span'):
        text = span.get_text()
        if not text:
            continue
        classes = set()
        if 'class' in span.attrs:
            classes = set(span['class'])
        if css_classes['bold'] & classes:
            text = highlight_text(text, '**')
        if css_classes['italic'] & classes:
            text = highlight_text(text, '//')
        span.replace_with(text)

    # handle unordered lists
    for ul in soup.find_all('ul'):
        text = ''
        for li in ul.find_all('li'):
            text += '* ' + replace_newline(li.get_text()) + '\n'
        ul.replace_with(text)

    # handle ordered lists
    for ol in soup.find_all('ol'):
        text = ''
        for li in ol.find_all('li'):
            text += '# ' + replace_newline(li.get_text()) + '\n'
        ol.replace_with(text)


    for p in soup.find_all('p'):
        classes = set(p['class'])
        text = p.get_text().strip()
        text = replace_newline(text) + '\n\n'
        if 'title' in classes:
            text = '+ ' + text
        p.replace_with(text)

    # handle horizontal rules/page breaks
    for hr in soup.find_all('hr'):
        hr.replace_with('----')

    # handle tables
    for table in soup.find_all('table'):
        text = ''
        for tr in table.find_all('tr'):
            text += '||'
            for td in tr.find_all('td'):
                text += td.get_text().strip() + '||'
            text += '\n'
        table.replace_with(text)

    wikidot = soup.get_text()
    # clean up
    wikidot = re.sub(r'^\s*$', '', wikidot, flags=re.MULTILINE)
    wikidot = re.sub(r'\n\n\n*', '\n\n', wikidot)
    return wikidot, images

def append_credits(wikidot, title, author, year, url):
    wikidot += f'\n++ Credits\n{title} was written by {author} for the {year} Shotgun Scenario contest.\nSource: {url}'
    return wikidot

def convert_html(html_path, out_path, credits_data=None, img_prefix=''):
    html = open(html_path).read()
    soup = BeautifulSoup(html, 'lxml')
    wikidot, images = soup_to_wikidot(soup, img_prefix=img_prefix)
    if credits_data is not None:
        title, author, year, url = credits_data
        wikidot = append_credits(wikidot, title, author, year, url)
    with open(out_path, 'w') as wikidot_file:
        wikidot_file.write(wikidot)
    if images:
        out_dir = os.path.dirname(out_path)
        for img_name, img_data in images:
            img_path = f'{out_dir}/{img_name}'
            with open(img_path, 'wb') as img_file:
                img_file.write(img_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('html_file')
    parser.add_argument('out_file')
    args = parser.parse_args()

    convert_html(args.html_file, args.out_file)

