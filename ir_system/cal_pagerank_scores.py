import os
import pickle
import networkx as nx
import json
from nltk.corpus import stopwords

stop_words = list(set(stopwords.words('english')))


def read_files():
    corpus = []
    url_title_map = {}
    url_content_map = {}

    cur_dir = os.path.dirname(__file__)
    relative_path = '../crawler/crawler/4000.json'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path) as f:
        data = json.load(f)
    for page in data:
        corpus.append(page['url'])
        url_title_map[page['url']] = page['title']
        url_content_map[page['url']] = page['content']
    return corpus, data, url_title_map, url_content_map


def create_graphs(corpus):
    """ Creates graphs for all documents
    input: list of tokens
    output: list of graphs, one for each document
    """
    G = nx.DiGraph()
    for url in corpus:
        G.add_node(url)
    return G


def add_edges(G, corpus):
    """ adds edges to the nodes in a graph
    input: document ngrams, graphs for each document
    output: updated graph for each document"""

    for page in corpus:
        for link in page['outlinks']:
            if link != page['url']:
                if not G.has_edge(page['url'], link):
                    G.add_edge(page['url'], link)
    return G


def pagerank(G):
    """runs pagerank algorithm and returns scores for each node in each document's graph
    input: graph for each document
    output: scores for each document"""
    node_scores = {}
    url_index_map = {}
    epsilon = 0.85
    p = 1 / len(G)
    count = 0
    for node in G.nodes():
        node_scores[node] = p
        url_index_map[count] = node
        count += 1

    for _ in range(10):
        for node in G.nodes():
            result = 0
            for predecessor in G.predecessors(node):
                result += node_scores[predecessor] / len(set(G.successors(predecessor)))
            node_scores[node] = (epsilon / len(set(G))) + (1 - epsilon) * result
    return node_scores, url_index_map


def main():
    corpus, data, url_title_map, url_content_map = read_files()
    graph = create_graphs(corpus)
    graph = add_edges(graph, data)
    node_scores, url_index_map = pagerank(graph)

    cur_dir = os.path.dirname(__file__)

    relative_path = '../pickles/node_scores.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(node_scores, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/url_index_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(url_index_map, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/url_title_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(url_title_map, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/url_content_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(url_content_map, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
