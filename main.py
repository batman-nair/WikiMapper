from multiprocessing import Pool

import src.wiki_util as wiki_util

def process_interlink_scores(target_link: str, all_links: set):
    interlink_scores = {}
    with open('source_links', 'w', encoding='utf-8') as source_file:
        source_file.write(target_link)

    pool = Pool(10)
    for depth in range(1, 2):
        with open('source_links', 'r', encoding='utf-8') as source_file, open('generated_links', 'w', encoding='utf-8') as generated_file:
            for extracted_links in pool.imap(wiki_util.extract_wiki_links, source_file):
                generated_file.write('\n'.join(extracted_links))

        with open('generated_links', 'r', encoding='utf-8') as generated_file, open('source_links', 'w', encoding='utf-8') as source_file:
            for link in generated_file:
                link = link.strip()
                if link in all_links:
                    interlink_scores[link] = interlink_scores.get(link, 0) + 1/depth
                else:
                    source_file.write(link+'\n')

    return interlink_scores

if __name__ == '__main__':
    country_links = []
    with open('country_links.txt', 'r') as countries_file:
        country_links = set(countries_file.read().splitlines())

    country_scores = process_interlink_scores('https://en.wikipedia.org/wiki/Australia', country_links)

    for country, score in country_scores.items():
        print(country, score)
