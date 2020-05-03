import json
import string
import re
import math

import nltk
from nltk.corpus import stopwords

stop_words = list(set(stopwords.words('english')))
from nltk.stem import PorterStemmer

weight_squares = []


def read_files():
    corpus = []

    with open('crawler/crawler/data.json') as f:
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
        tokens = []
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
        cleaned_tokens = []
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
        stemmed_tokens = []
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
        new_words = []
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
                temp[i + 1] = 1
                inverted_index[word] = temp
            else:
                if i + 1 not in inverted_index[word]:
                    inverted_index[word][i + 1] = 1
                else:
                    inverted_index[word][i + 1] += 1
    return inverted_index


def cal_document_weights(inverted_index, collection):
    """Returns document weights

        input: inverted index, collection
        output: document weights
    """
    document_weights = {}
    global weight_squares
    for i, document in enumerate(collection):
        temp = {}
        weights_sum = 0
        for word in document:
            if word not in temp:
                # weight = tf * idf
                temp[word] = (inverted_index[word][i + 1] / len(document)) * math.log2(
                    len(collection) / len(inverted_index[word]))
                weights_sum += math.pow(temp[word], 2)
        weight_squares.append(weights_sum)
        document_weights[i + 1] = temp
    return document_weights

def cal_query_weights(query_terms, inverted_index, collection):
    """ Calculates and returns query weights
    """
    query_weights = {}
    for i, query in enumerate(query_terms):
        query_token_weights = {}
        for term in query:
            if term in inverted_index:
                tf = query.count(term)/len(query)
                idf = math.log2(len(collection)/len(inverted_index[term]))
                tf_idf = tf * idf
                query_token_weights[term] = tf_idf
        query_weights[i+1] = query_token_weights
    return query_weights

def cal_cosine_similarity(query_list, collection, document_weights, query_weights):
    """ Calculates and returns cosine similarities
    """
    global weight_squares
    cosine_similarities_list = {}
    for i, query in enumerate(query_list):
        query_doc_cosine_similarities = {}
        for j, document in enumerate(collection):
            common_terms = list(set(query)&set(document))
            query_document_weights_sum = 0
            if common_terms:
                for term in common_terms:
                    # Numerator
                    query_document_weights_sum += query_weights[i+1][term] * document_weights[j+1][term]
                # Cosine similarities = Numerator / Denominator
                query_doc_cosine_similarities[j+1] = query_document_weights_sum/math.sqrt(weight_squares[j])
        cosine_similarities_list[i+1] = query_doc_cosine_similarities
    return cosine_similarities_list

def sort_cosine_similarities(cosine_similarities):
    """Sorts and returns a list of cosine similarities in decreasing order"""

    sorted_cosine_similarities = {}
    for query in cosine_similarities:
        # Sort the dictionary by value (item[1])
        # Reverse = True because we want to sort it by decreasing order
        # Documents which are most similar to query are on top
        sorted_ = sorted(cosine_similarities[query].items(), key=lambda item: item[1], reverse=True)
        sorted_cosine_similarities[query] = sorted_
    return sorted_cosine_similarities


corpus = read_files()
corpus = preprocess_data(corpus)
terms = tokenize_data(corpus)
terms = eliminate_stopwords(terms)
terms = stem_tokens(terms)
terms = eliminate_stopwords(terms)
terms = eliminate_one_two_character_words(terms)
inverted_index = build_inverted_index(terms)
document_weights = cal_document_weights(inverted_index, terms)
queries = ["Computer Science"]
queries = preprocess_data(queries)
query_terms = tokenize_data(queries)
query_terms = eliminate_stopwords(query_terms)
query_terms = stem_tokens(query_terms)
query_terms = eliminate_stopwords(query_terms)
query_terms = eliminate_one_two_character_words(query_terms)
query_weights = cal_query_weights(query_terms, inverted_index, terms)
cosine_similarities = cal_cosine_similarity(query_terms, terms, document_weights, query_weights)
sorted_cosine_similarities = sort_cosine_similarities(cosine_similarities)
print(sorted_cosine_similarities)

