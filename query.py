import sys
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from ctypes import ArgumentError
from file_io import *

class Query:
    """
    Class that parses in arguments of the previously indexed files and an optional
    argument that says to use PageRank. Also, runs a REPL to take in and process 
    search queries submitted by users. For valid queries, returns a list of the 
    top ten documents scored based on term relevance and PageRank if specified.
    """
    def __init__(self, args):
        self.pagerank = False
        self.title_file, self.docs_file, self.words_file = self.process_arguments(args)  
       
    def process_arguments(self, args):
        """Returns a list of [title file, docs file, words file] if command
        line arguments are valid, otherwise raises an exception. If the 
        PageRank argument is specified, the value of the boolean variable
        pagerank is set to True.
        
        Parameters:
        args -- list of command line arguments 

        Returns:
        A list of title file, docs file, and words file

        Throws:
        ArgumentError if the command line arguments are invalid 
        """
       
        file_list = []
        if len(args) == 4 and args[0] == '--pagerank':
            # do pagerank
            self.pagerank = True
            file_list = args[1:]
        elif len(args) == 3:
            # we don't do pagerank
           file_list = args
        else:
            raise ArgumentError("Invalid command line arguments, try again.")

        return file_list
 

    def calc_score(self, pagerank_score, rel_score) -> float:
        """Calculates score by multiplying the pagerank score times the relevance 
        score if PageRank is specified, otherwise returns just the relevance
        score.
      
        Parameters:
        pagerank_score -- pagerank score
        rel_score -- relevance score

        Returns:
        A float (document score)
        """

        if self.pagerank:
            return pagerank_score * rel_score
        else:
            return rel_score
           

    def retrieve_results(self, words: list) -> list:
        """Uses proccesed words from search query to calculate document score to return a 
        list of the top, maximum of ten, documents 

        Parameters:
        words -- list of proccessed words from search query 

        Returns:
        A list of page titles corresponding to the top ten highest scoring documents
        """
        ids_to_titles = {}
        read_title_file(self.title_file, ids_to_titles)

        words_to_relevance_dict = {}
        read_words_file(self.words_file, words_to_relevance_dict)

        ids_to_pagerank = {}
        read_docs_file(self.docs_file, ids_to_pagerank)

        ids_to_total_relevance = {}

        for word in words:
            if word in words_to_relevance_dict:
                for kvpair in words_to_relevance_dict[word].items():
                    if kvpair[0] not in ids_to_total_relevance:
                        ids_to_total_relevance[kvpair[0]] = self.calc_score(ids_to_pagerank[kvpair[0]], kvpair[1])
                    else:
                        ids_to_total_relevance[kvpair[0]] += self.calc_score(ids_to_pagerank[kvpair[0]], kvpair[1]) 
        
        sorted_ids = sorted(ids_to_total_relevance.items(), key=lambda x: x[1], reverse=True)
        results = []
        num_results = len(sorted_ids)
        num_results_to_return = min(10, num_results)
        for i in range(num_results_to_return):
            results.append(ids_to_titles[sorted_ids[i][0]])
        return results

    def processed_search_terms(self, search_terms: str) -> list:
        """Processes query inputted by users through tokenizing, removing stop words, and stemming
       
        Parameters:
        search_terms -- str inputted by user 

        Returns:
        A list of processed words 
        """
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        processed_words = []

        tokens = re.findall(n_regex, search_terms)
        for wrd in tokens:
            if wrd.lower() not in STOP_WORDS:
                processed_words.append(stemmer.stem(wrd.lower()))

        return processed_words

    def print_results(self, search_terms: str):
        """Passes the user query into helper methods to print the top results (max
        of ten), or an informative message if no results

        Parameters:
        search_terms -- str inputted by user 

        Returns:
        Prints list of page titles corresponding to the top (max ten) documents
        or a message if the query returns no results
        
        """
        results = self.retrieve_results(self.processed_search_terms(search_terms))

        if not results:
            print("No results for that search.")
        
        for idx, result in enumerate(results):
            print(str(idx + 1) + " " + result)

if __name__ == "__main__":
    """
    Sets up REPL interface for users to search documents.
    Instantiates a Query object to process the queries submitted by user. 
    """
    q = Query(sys.argv[1:])

    while True is True:
        response = input("Search for pages here: ")
        if response == ':quit':
            break
        q.print_results(response)