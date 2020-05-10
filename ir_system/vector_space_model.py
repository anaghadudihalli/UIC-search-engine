import json
import os
import string
import re
import math
import pickle

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

stop_words = list(set(stopwords.words('english')))


def read_files():
    corpus = []
    cur_dir = os.path.dirname(__file__)
    relative_path = '../crawler/crawler/4000.json'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path) as f:
        data = json.load(f)

    for page in data:
        corpus.append(page['title'].strip() + ' ' + page['content'].strip())
    return corpus


def preprocess_data(collection):
    """Preprocesses the data. Turns all words into lowercase, removes punctuation, digits and leading and trailing whitespaces.

        input: unprocessed data
        output: preprocessed data
    """
    for i in range(len(collection)):
        collection[i] = collection[i].translate(str.maketrans('', '', string.punctuation))
        collection[i] = re.sub("\d+", "", collection[i])
        collection[i] = " ".join(collection[i].split())
        collection[i] = collection[i].lower()
        collection[i] = collection[i].strip()
    return collection


def tokenize_data(collection):
    """Returns a list of tokens from the input using NLTK's word_tokenize()

        input: string of data
        output: list of tokens
    """
    result = []
    for document in collection:
        tokens = nltk.word_tokenize(document)
        result.append(tokens)
    return result


def eliminate_stopwords(tokenized_collection):
    """Returns a list of filtered tokens - that are not stop words

        input: list of tokens
        output: list of tokens excluding the stop words
    """
    global stop_words
    result = []
    for document in tokenized_collection:
        cleaned_tokens = [word for word in document if word not in stop_words]
        result.append(cleaned_tokens)
    return result


def stem_tokens(tokenized_collection):
    """Returns a list of stemmed_tokens after performing Porter Stemming on tokens

        input: list of tokens
        output: list of stemmed tokens
    """
    stemmer = PorterStemmer()
    result = []
    for document in tokenized_collection:
        stemmed_tokens = [stemmer.stem(word) for word in document]
        result.append(stemmed_tokens)
    return result


def eliminate_one_two_character_words(collection):
    """Returns a list of terms that consist more than 2 characters

        input: list of terms
        output: list of terms that consist more than 2 characters
    """
    result = []
    for document in collection:
        new_words = [word for word in document if len(word) > 2]
        result.append(new_words)
    return result


def build_inverted_index(collection):
    """Returns inverted index

        input: tokenized documents
        output: inverted index
    """
    inverted_index = {}
    for i, document in enumerate(collection):
        for word in document:
            if word not in inverted_index:
                temp = {}
                temp[i] = 1
                inverted_index[word] = temp
            else:
                if i not in inverted_index[word]:
                    inverted_index[word][i] = 1
                else:
                    inverted_index[word][i] += 1
    return inverted_index


def cal_document_weights(inverted_index, collection):
    """Returns document weights

        input: inverted index, collection
        output: document weights
    """
    document_weights = {}
    weight_squares = []
    for i, document in enumerate(collection):
        temp = {}
        weights_sum = 0
        for word in document:
            if word not in temp:
                temp[word] = (inverted_index[word][i] / len(document)) * math.log2(
                    len(collection) / len(inverted_index[word]))
                weights_sum += math.pow(temp[word], 2)
        weight_squares.append(weights_sum)
        document_weights[i] = temp
    return document_weights, weight_squares


def cal_query_weights(query_terms, inverted_index, collection):
    """ Calculates and returns query weights
    """
    query_weights = {}
    for i, query in enumerate(query_terms):
        query_token_weights = {}
        for term in query:
            if term in inverted_index:
                tf = query.count(term) / len(query)
                idf = math.log2(len(collection) / len(inverted_index[term]))
                tf_idf = tf * idf
                query_token_weights[term] = tf_idf
        query_weights[i] = query_token_weights
    return query_weights


def cal_cosine_similarity(query_list, collection, document_weights, query_weights, weight_squares_list):
    """ Calculates and returns cosine similarities
    """
    cosine_similarities_list = {}
    for i, query in enumerate(query_list):
        query_doc_cosine_similarities = {}
        for j, document in enumerate(collection):
            common_terms = list(set(query) & set(document))
            query_document_weights_sum = 0
            if common_terms:
                for term in common_terms:
                    query_document_weights_sum += query_weights[i][term] * document_weights[j][term]
                query_doc_cosine_similarities[j] = query_document_weights_sum / math.sqrt(weight_squares_list[j])
        cosine_similarities_list[i] = query_doc_cosine_similarities
    return cosine_similarities_list


def sort_cosine_similarities(cosine_similarities, n):
    """Sorts and returns a list of cosine similarities in decreasing order"""

    sorted_cosine_similarities = {}
    for query in cosine_similarities:
        # Sort the dictionary by value (item[1])
        # Reverse = True because we want to sort it by decreasing order
        # Documents which are most similar to query are on top
        sorted_ = sorted(cosine_similarities[query].items(), key=lambda item: item[1], reverse=True)[:n]
        sorted_cosine_similarities[query] = sorted_
    return sorted_cosine_similarities


def main():
    corpus = read_files()
    corpus = preprocess_data(corpus)
    terms = tokenize_data(corpus)
    terms = eliminate_stopwords(terms)
    terms = stem_tokens(terms)
    terms = eliminate_stopwords(terms)
    terms = eliminate_one_two_character_words(terms)
    inverted_index = build_inverted_index(terms)
    document_weights, weight_squares = cal_document_weights(inverted_index, terms)

    cur_dir = os.path.dirname(__file__)
    relative_path = '../pickles/terms.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(terms, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/inverted_index.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(inverted_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/document_weights.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(document_weights, handle, protocol=pickle.HIGHEST_PROTOCOL)

    relative_path = '../pickles/weight_squares.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'wb+') as handle:
        pickle.dump(weight_squares, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
