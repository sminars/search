import sys
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from ctypes import ArgumentError
from file_io import *

# class PageRelevance:
#     def __init__(self, key, value):
#         self.page_id = key
#         self.relevance = value

class Query:
    def __init__(self, args):
        self.title_file, self.docs_file, self.words_file = self.process_arguments(args)  

    def process_arguments(self, args):
        """returns a list of [title file, docs file, words file] if command
        line arguments are valid, otherwise raises an exception"""
        file_list = []
        if len(args) == 4 and args[0] == '--pagerank':
            # do pagerank
            file_list = args[1:]
        elif len(args) == 3:
            # we don't do pagerank
            file_list = args
        else:
            raise ArgumentError("Invalid command line arguments, try again.")

        return file_list

    def processed_search_terms(self, search_terms: str) -> list:
        """blah"""
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        processed_words = []

        tokens = re.findall(n_regex, search_terms)
        for wrd in tokens:
            if wrd.lower() not in STOP_WORDS:
                processed_words.append(stemmer.stem(wrd.lower()))

        return processed_words

    def retrieve_results(self, words: list) -> list:
        """takes in list of processed words and returns a list of page titles"""
        ids_to_titles = {}
        read_title_file(self.title_file, ids_to_titles)

        words_to_relevance_dict = {}
        read_words_file(self.words_file, words_to_relevance_dict)

        ids_to_total_relevance = {}
        
        for word in words:
            if word in words_to_relevance_dict:
                for kvpair in words_to_relevance_dict[word].items():
                    if kvpair[0] not in ids_to_total_relevance:
                        ids_to_total_relevance[kvpair[0]] = kvpair[1]
                    else:
                        ids_to_total_relevance[kvpair[0]] += kvpair[1]

        sorted_ids = sorted(ids_to_total_relevance.items(), key=lambda x: x[1], reverse=True)
        results = []
        num_results = len(sorted_ids)
        num_results_to_return = min(10, num_results)
        for i in range(num_results_to_return):
            results.append(ids_to_titles[sorted_ids[i][0]])

        return results
                    

        # want a structure that can be ordered, and that for each element, it
        # has the page id and the relevance score bundled together, but mutable


    def print_results(self, search_terms: str):
        """passes the query into helper methods and prints the top results (max
        of 10), or an informative message if no results"""
        results = self.retrieve_results(self.processed_search_terms(search_terms))

        if not results:
            print("No results for that search.")
        
        for idx, result in enumerate(results):
            print(str(idx + 1) + " " + result)


if __name__ == "__main__":
    q = Query(sys.argv[1:])

    while True is True:
        response = input("Search for pages here: ")
        if response == ':quit':
            break
        q.print_results(response)