import os
from multiprocessing import Pool, cpu_count

import src.wiki_util as wiki_util

def process_interlink_scores(target_link: str, all_links: set, max_depth: int = 2):
    interlink_scores = {}
    with open('source_links', 'w', encoding='utf-8') as source_file:
        source_file.write(target_link)

    pool = Pool(cpu_count()*2)
    for depth in range(1, max_depth+1):
        print('Parsing at depth', depth)
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

def generate_link_to_name_map(all_links):
    pool = Pool(cpu_count()*2)
    link_to_name_list = pool.map(wiki_util.get_page_title, all_links)
    link_to_name_map = dict(link_to_name_list)
    return link_to_name_map

if __name__ == '__main__':
    all_links = []
    output_directory = 'csv'
    with open('countries/country_links.txt', 'r') as countries_file:
        all_links = set(countries_file.read().splitlines())

    link_to_name_map = generate_link_to_name_map(all_links)
    link_total_scores = dict()

    os.makedirs(output_directory, exist_ok=True)

    for link in all_links:
        current_scores = process_interlink_scores(link, all_links, max_depth=2)
        print('Calculated scores for', link_to_name_map[link], ', writing to csv file.')
        csv_file = os.path.join(output_directory, link_to_name_map[link]+'.csv')
        total_score = 0
        with open(csv_file, 'w', encoding='utf-8') as score_file:
            score_file.write('Source,Target,Weight\n')
            link_name = link_to_name_map[link]
            for link, score in current_scores.items():
                total_score += score
                connection_name = link_to_name_map[link]
                score_file.write(','.join([link_name, connection_name, str(score)]) + '\n')
        link_total_scores[link_to_name_map[link]] = total_score

    with open(os.path.join(output_directory, 'node_list'), 'w') as node_file:
        node_file.write('Id,Label,Count')
        for entry_name, total_score in entry_total_scores.items():
            node_file.write(','.join(entry_name, entry_name, int(total_score)))