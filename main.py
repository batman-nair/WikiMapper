import requests
from bs4 import BeautifulSoup

def is_non_meta_link(link):
    meta_flags = ['Wikipedia:', 'Category:', 'Image:', 'Talk:', 'Portal:', 'Help:', 'Special:', 'Book:', 'Template:', 'Template_talk:']
    link_href = link.get('href', '')
    has_meta_link = any([meta_flag in link_href for meta_flag in meta_flags])
    return not has_meta_link and not link.get('class', False)

def extract_wiki_links(url: str):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    content_body = soup.find(id='mw-content-text')
    for naviagtion_section in content_body.find_all(role='navigation'):
        naviagtion_section.decompose()

    article_links = [link for link in content_body.find_all('a') if link.get('href', '').startswith('/wiki')]
    filtered_links = filter(is_non_meta_link, article_links)
    wiki_links = map(lambda link: 'https://en.wikipedia.org'+link.get('href'), filtered_links)
    return list(wiki_links)

wiki_links = extract_wiki_links('https://en.wikipedia.org/wiki/List_of_sovereign_states')
with open('country_links', 'w') as ff:
    ff.write('\n'.join(wiki_links))
print('\n'.join(wiki_links))
