# index.py
from ctypes import ArgumentError
import sys
import re
import math
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import file_io

class IndexInfo:
    def __init__(self, idf_arr, max_per_row, word_counts):
        self.idf_array = idf_arr
        self.max_frequency_per_row = max_per_row
        self.word_counts = word_counts


class Indexer:
    def __init__(self, args):
        if len(args) != 4:
            raise ArgumentError("Must have exactly 4 arguments after index.py -- try again.")
        
        xml_file = args[0]
        self.title_file = args[1]
        self.docs_file = args[2]
        self.words_file = args[3]

        root: "Element" = et.parse(xml_file).getroot()
        self.page_ids = []  # list of tuples with (page ID, page title)
        self.n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        self.corpus = {} # keys = words, values = indices
        self.corpus_index = 0  
        self.tf_array = []
        self.idf_array = []
        self.relevance = []

        # ii = self.make_corpus(root.findall("page"))
        # rel_array = self.make_relevance(ii)
        # words_to_rel = self.make_wtr_dict(rel_array)

        self.make_corpus(root.findall("page"))
        self.calculate_relevance()
        self.write_files(self.title_file, self.words_file)

        # should creating an indexer do everything, or just initialize the vars?
          
    def add_to_corpus(self, words: str, info: list, idf: list):
        """tokenizes, lower cases, and stems the elements of words and adds non-
        stop words to self.corpus
        
        parameters:
        info - two-element list where index 0 is a row of word counts and index 1 is an
        int representing the current maximum word count in that row
        idf - list where we keep track of the number of documents each word 
        appears in
        """
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        tokens = re.findall(self.n_regex, words)

        for wrd in tokens:
            if wrd.lower() not in STOP_WORDS:
                stemmed_wrd = stemmer.stem(wrd.lower())
                if stemmed_wrd not in self.corpus:
                    self.corpus[stemmed_wrd] = self.corpus_index
                    self.corpus_index += 1
                    # also add a new column in page row and in word_counts
                    info[0].append(1)
                    idf.append(1)
                    for row in self.tf_array:
                        row.append(0)
                else:  # the word is in the corpus
                    # increment the word count for this word in this page
                    info[0][self.corpus[stemmed_wrd]] += 1

                    # if this is the first time we've seen this word in this row
                    if info[0][self.corpus[stemmed_wrd]] == 1:
                        # increment this word's idf n_i count
                        idf[self.corpus[stemmed_wrd]] += 1

                # update maximum value of this row
                if info[0][self.corpus[stemmed_wrd]] > info[1]:
                    info[1] = info[0][self.corpus[stemmed_wrd]]
        

    def make_corpus(self, pages : list):
        """takes in xml pages and populates global variable corpus"""        
       
        id2pn = {}  # page ids to list of names of pages linked to
        max_in_each_row = [] # keeps track of frequency of most frequent word for each page
        idf_arr = [] # keeps track of n_i counts for each word in corpus

        for page in pages:
            pid = int(page.find('id').text.strip())
            title = page.find('title').text.strip()
            self.page_ids.append((pid, title))
            id2pn[pid] = []
            page_row = [0] * len(self.corpus)
            # two-element list: first element is a list of word counts for the 
            # page, and the second element is the most common word's frequency
            page_info = [page_row, 0]
            
            page_words = re.findall(self.n_regex, page.find('title').text + " " + page.find('text').text)

            for word in page_words: # "this", then "is", then "a"....
                if re.match('\[\[[^\[]+?\]\]', word):
                    w = word[2:-2]
                    if '|' in w:
                        link_page, link_text = w.split('|', 1)
                        id2pn[pid].append(link_page.lower())
                        self.add_to_corpus(link_text, page_info, idf_arr)
                    elif ':' in w:
                        id2pn[pid].append(w)  # we aren't sure if category pages should count as links
                        w = w.replace(":", " ")
                        self.add_to_corpus(w, page_info, idf_arr)
                    else:  # links where the text is the name of the page
                        id2pn[pid].append(w)
                        self.add_to_corpus(w, page_info, idf_arr)
                else:  # i.e. if the word is not a link
                    self.add_to_corpus(word, page_info, idf_arr)

            self.tf_array.append(page_info[0])
            max_in_each_row.append(page_info[1])
                
        self.calculate_tf(max_in_each_row)
        self.calculate_idf(idf_arr)

        # could we instead make this function take in the list of pages and 
        # return idf_arr and max_in_each_row and tf_array and id2pn?
        

    def calculate_tf(self, maxs: list):
        for idx, row in enumerate(self.tf_array):
            self.tf_array[idx] = [wc / maxs[idx] for wc in row]

    def calculate_idf(self, n_i_list: list):
        n = len(self.page_ids)
        self.idf_array = [math.log(n / n_i) for n_i in n_i_list]
    
    def calculate_relevance(self):
        for r in self.tf_array:
            self.relevance.append([elem * self.idf_array[idx] for idx, elem in enumerate(r)])

    def write_files(self, title_file: str, words_file: str):
        words_to_relevance = {}

        # this should go in a method that takes in a relevance array and returns
        # a words to relevance dictionary
        for col_idx, word in enumerate(self.corpus.keys()):
            ids_to_relevance = {}
            for row_idx in range(len((self.relevance))):
                page_id = self.page_ids[row_idx][0]
                ids_to_relevance[page_id] = self.relevance[row_idx][col_idx]

            words_to_relevance[word] = ids_to_relevance

        # pass words_to_relevance into file_io to write to words file
        file_io.write_words_file(words_file, words_to_relevance)
        # convert page_ids to dictionary and write to title file
        file_io.write_title_file(title_file, dict(self.page_ids))


if __name__ == "__main__":
    """this should be the "view" of the model view controller"""
    idxr = Indexer(sys.argv[1:])
    print("File successfully indexed!")
