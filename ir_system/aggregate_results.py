import os

from ir_system.vector_space_model import preprocess_data, tokenize_data, eliminate_stopwords, stem_tokens, \
    eliminate_one_two_character_words, cal_cosine_similarity, \
    cal_query_weights
import pickle


def load_pickles():
    cur_dir = os.path.dirname(__file__)

    relative_path = '../pickles/terms.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        terms = pickle.load(handle)

    relative_path = '../pickles/inverted_index.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        inverted_index = pickle.load(handle)

    relative_path = '../pickles/document_weights.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        document_weights = pickle.load(handle)

    relative_path = '../pickles/weight_squares.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        weight_squares = pickle.load(handle)

    relative_path = '../pickles/node_scores.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        node_scores = pickle.load(handle)

    relative_path = '../pickles/url_index_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        url_index_map = pickle.load(handle)

    return terms, inverted_index, document_weights, weight_squares, node_scores, url_index_map


def combine_pagerank_tfidf(cosine_similarities, node_scores, url_index_map):
    score = {}
    for key, value in cosine_similarities[0].items():
        score[url_index_map[key]] = 0.80 * value + 0.20 * node_scores[url_index_map[key]]
    return score


def get_results(query, number_of_links):
    terms, inverted_index, document_weights, weight_squares, node_scores, url_index_map = load_pickles()
    queries = [query]
    queries = preprocess_data(queries)
    query_terms = tokenize_data(queries)
    query_terms = eliminate_stopwords(query_terms)
    query_terms = stem_tokens(query_terms)
    query_terms = eliminate_stopwords(query_terms)
    query_terms = eliminate_one_two_character_words(query_terms)
    query_weights = cal_query_weights(query_terms, inverted_index, terms)
    cosine_similarities = cal_cosine_similarity(query_terms, terms, document_weights, query_weights, weight_squares)
    score = combine_pagerank_tfidf(cosine_similarities, node_scores, url_index_map)
    sorted_results = sorted(score.items(), key=lambda item: item[1], reverse=True)[:number_of_links]
    return sorted_results


def main():
    pass


if __name__ == '__main__':
    main()
