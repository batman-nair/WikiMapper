import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

def is_non_meta_link(link):
    meta_flags = ['Wikipedia:', 'Category:', 'Image:', 'Talk:', 'Portal:', 'Help:', 'Special:', 'Book:', 'Template:', 'Template_talk:']
    link_href = link.get('href', '')
    has_meta_link = any([meta_flag in link_href for meta_flag in meta_flags])
    return not has_meta_link and not link.get('class', False)

def extract_wiki_links(url: str):
    url = url.strip()
    print('Parsing link', url)
    wiki_page = requests.get(url)
    soup = BeautifulSoup(wiki_page.content, 'html.parser')
    content_body = soup.find(id='mw-content-text')
    for naviagtion_section in content_body.find_all(role='navigation'):
        naviagtion_section.decompose()

    article_links = [link for link in content_body.find_all('a') if link.get('href', '').startswith('/wiki')]
    filtered_links = filter(is_non_meta_link, article_links)
    wiki_links = map(lambda link: 'https://en.wikipedia.org'+link.get('href'), filtered_links)
    return list(wiki_links)

if __name__ == '__main__':
    country_links = []
    with open('country_links.txt', 'r') as countries_file:
        country_links = set(countries_file.read().splitlines())

    country_scores = {}
    with open('source_links', 'w', encoding='utf-8') as source_file:
        source_file.write('https://en.wikipedia.org/wiki/Australia')

    pool = Pool(10)

    for depth in range(1, 3):
        with open('source_links', 'r', encoding='utf-8') as source_file, open('generated_links', 'w', encoding='utf-8') as generated_file:
            for extracted_links in pool.imap(extract_wiki_links, source_file):
                generated_file.write('\n'.join(extracted_links))

        with open('generated_links', 'r', encoding='utf-8') as generated_file, open('source_links', 'w', encoding='utf-8') as source_file:
            for link in generated_file:
                link = link.strip()
                if link in country_links:
                    country_scores[link] = country_scores.get(link, 0) + 1/depth
                else:
                    source_file.write(link+'\n')

    for country, score in country_scores.items():
        print(country, score)
