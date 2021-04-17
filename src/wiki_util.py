import re
import functools
import requests
from bs4 import BeautifulSoup

def _is_non_meta_link(link):
    meta_flags = ['Wikipedia:', 'Category:', 'Image:', 'Talk:', 'Portal:', 'Help:', 'Special:', 'Book:', 'Template:', 'Template_talk:']
    link_href = link.get('href', '')
    has_meta_link = any([meta_flag in link_href for meta_flag in meta_flags])
    return not has_meta_link and not link.get('class', False)

@functools.lru_cache(maxsize=500)
def extract_wiki_links(url: str):
    url = url.strip()
    print('Parsing link', url)
    wiki_page = requests.get(url)
    soup = BeautifulSoup(wiki_page.content, 'html.parser')
    content_body = soup.find(id='mw-content-text')
    for naviagtion_section in content_body.find_all(role='navigation'):
        naviagtion_section.decompose()

    article_links = [link for link in content_body.find_all('a') if link.get('href', '').startswith('/wiki')]
    filtered_links = filter(_is_non_meta_link, article_links)
    wiki_links = map(lambda link: 'https://en.wikipedia.org'+link.get('href'), filtered_links)
    return list(wiki_links)

def get_clean_page_title(url: str):
    print('Fetching page title', url)
    url = url.strip()
    wiki_page = requests.get(url)
    soup = BeautifulSoup(wiki_page.content, 'html.parser')
    page_title = soup.title.text[:-12] # Remove ' - Wikipedia' from title
    page_title = page_title.strip()
    page_title = re.sub(r'[\\;/]', '_', page_title)
    return (url, page_title)
