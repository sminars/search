import sys
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from ctypes import ArgumentError
from file_io import *

class Query:
    """
    Class that parses in arguments of the previously indexed files and an 
    optional argument that says to use PageRank. Also, runs a REPL to take in 
    and process search queries submitted by users. For valid queries, returns a 
    list of the top 10 documents by term relevance (and PageRank, if specified).
    """
    def __init__(self, args):
        self.pagerank = False
        self.t_file, self.d_file, self.w_file =  self.process_arguments(args)

        self.ids_to_titles = {}
        read_title_file(self.t_file, self.ids_to_titles)

        self.words_to_relevance = {}
        read_words_file(self.w_file, self.words_to_relevance)

        self.ids_to_pagerank = {}
        read_docs_file(self.d_file, self.ids_to_pagerank)
       
    def process_arguments(self, args):
        """Returns a tuple of (title file, docs file, words file) if command
        line arguments are valid, otherwise raises an exception. If the 
        PageRank argument is specified, the value of the boolean variable
        pagerank is set to True.
        
        Parameters:
        args -- list of command line arguments 

        Returns:
        A tuple of title file, docs file, and words file

        Throws:
        ArgumentError if the command line arguments are invalid 
        """
       
        file_list = []
        if len(args) == 4 and args[0] == '--pagerank':
            # do pagerank
            self.pagerank = True
            file_list = args[1:]
        elif len(args) == 3 and all([arg[-4:] == '.txt' for arg in args]):
            # we don't do pagerank
           file_list = args
        else:
            raise ArgumentError

        return file_list

    def calc_score(self, pagerank_score, rel_score) -> float:
        """Calculates score by multiplying the pagerank score by the relevance 
        score if PageRank is specified, otherwise just the relevance score.
      
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
        """Uses proccesed words from search query to calculate document score to
        return a list of the top, maximum of ten, documents 

        Parameters:
        words -- list of proccessed words from search query 

        Returns:
        A list of page titles corresponding to the highest scoring documents
        """

        ids_to_total_score = {}

        for word in words:
            if word in self.words_to_relevance:
                for pid in self.words_to_relevance[word].keys():
                    rel = self.words_to_relevance[word][pid]
                    rnk = self.ids_to_pagerank[pid]
                    if pid not in ids_to_total_score:
                        ids_to_total_score[pid] = self.calc_score(rnk, rel)
                    else:
                        ids_to_total_score[pid] += self.calc_score(rnk, rel) 
        
        sorted_ids = sorted(ids_to_total_score.items(), key=lambda x: x[1], 
                    reverse=True)  # sort in descending order by score
        results = []
        num_results = len(sorted_ids)
        num_results_to_return = min(10, num_results)
        for i in range(num_results_to_return):
            results.append(self.ids_to_titles[sorted_ids[i][0]])
        return results

    def processed_terms(self, search_terms: str) -> list:
        """Processes query inputted by users through tokenizing, removing stop 
        words, and stemming.
       
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
        """Passes the user query into helper methods to print the top results 
        (maximum of ten), or an informative message if there are no results.

        Parameters:
        search_terms -- user-input string of search terms 

        Returns:
        Prints list of page titles corresponding to the top (max ten) documents
        or a message if the query returns no results
        
        """
        processed_terms = self.processed_terms(search_terms)
        results = self.retrieve_results(processed_terms)

        if not results:
            print("No results for that search.")
        
        for idx, result in enumerate(results):
            print(str(idx + 1) + " " + result)

if __name__ == "__main__":
    """
    Sets up REPL interface for users to search documents.
    Instantiates a Query object to process the queries submitted by user. 
    """
    try:
        q = Query(sys.argv[1:])

        while True is True:  # continue until break statement is reached
            response = input("Search for pages here: ")
            if response == ':quit':
                break
            q.print_results(response)
    except FileNotFoundError:
        print("File not found -- try again.")
    except ArgumentError:
        print("Invalid command line arguments, try again.  Arguments must take"
        + " the form: \n    --pagerank <title-file>.txt <docs-file>.txt" 
        + " <words-file>.txt \nwhere --pagerank is an optional argument.")

    