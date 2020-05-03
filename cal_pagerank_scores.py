import glob
import os
import platform
import networkx as nx
import json

import nltk
from nltk.corpus import stopwords

stop_words = list(set(stopwords.words('english')))
from nltk.stem import PorterStemmer
from nltk.tokenize import WhitespaceTokenizer
from nltk.util import ngrams


def read_files():
    corpus = []

    with open('crawler/crawler/data.json') as f:
        data = json.load(f)
    for page in data:
        corpus.append(page['url'])
    return corpus, data


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
    epsilon = 0.85
    p = 1 / len(G)
    for node in G.nodes():
        node_scores[node] = p
    for _ in range(10):
        for node in G.nodes():
            result = 0
            for predecessor in G.predecessors(node):
                result += node_scores[predecessor] / len(set(G.successors(predecessor)))
            node_scores[node] = (epsilon / len(set(G))) + (1 - epsilon) * result
    return node_scores


corpus, data = read_files()

graph = create_graphs(corpus)

graph = add_edges(graph, data)

node_scores = pagerank(graph)
print(node_scores)