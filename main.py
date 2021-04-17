import os
import argparse
from multiprocessing import Pool, cpu_count

import src.wiki_util as wiki_util

def process_interlink_scores(target_link: str, all_links: set[str], max_depth: int = 2, pool_size: int = 4):
    interlink_scores = {}
    with open('source_links', 'w', encoding='utf-8') as source_file:
        source_file.write(target_link)

    pool = Pool(pool_size)
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

def generate_link_to_name_map(all_links: set[str], pool_size: int = 4):
    pool = Pool(pool_size)
    link_to_name_list = pool.map(wiki_util.get_clean_page_title, all_links)
    link_to_name_map = dict(link_to_name_list)
    return link_to_name_map

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate csv of wiki links connection with weights based on number of direct/indirect connections between them.')
    parser.add_argument('-i', '--input', type=str, default='input.txt', help='path to file with links')
    parser.add_argument('-d', '--depth', type=int, default=2, help='maximum depth that should be parsed')
    parser.add_argument('-o', '--output', type=str, default='csv', help='output directory to store the csv files')
    parser.add_argument('-j', '--jobs', type=int, default=cpu_count()*2, help='Number of processes to spawn for parallel processing. Default is cpu_count*2')
    args = parser.parse_args()

    all_links = set()
    output_directory = args.output
    with open(args.input, 'r') as links_file:
        all_links = set(links_file.read().splitlines())

    link_to_name_map = generate_link_to_name_map(all_links, pool_size=args.jobs)
    link_total_scores = dict()

    os.makedirs(output_directory, exist_ok=True)

    for link in all_links:
        current_scores = process_interlink_scores(link, all_links, max_depth=args.depth, pool_size=args.jobs)
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

    with open(os.path.join(output_directory, 'node_list.csv'), 'w') as node_file:
        node_file.write('Id,Label,Count')
        for link_name, total_score in link_total_scores.items():
            node_file.write(','.join([link_name, link_name, int(total_score)]))