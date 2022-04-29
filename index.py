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
    def __init__(self, idf_arr, max_per_row, word_counts, weights, corpus):
        self.idf_array = idf_arr
        self.max_per_row = max_per_row
        self.word_counts = word_counts
        self.weights = weights
        self.corpus = corpus

class Indexer:
    def __init__(self, args):
        if len(args) != 4:
            raise ArgumentError("Must have exactly 4 arguments after index.py -- try again.")
        
        self.page_ids = []  # list of tuples with (page ID, page title)
        self.title_to_id = {} # look up page IDs by title
        self.id_to_index = {}
        self.n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        # self.corpus = {} # keys = words, values = indices
        self.corpus_index = 0  

        self.write_files(args[0], args[1], args[2], args[3])
          
    def add_to_corpus(self, words: str, info: list, idf: list, word_counts: list, corpus):
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
                if stemmed_wrd not in corpus:
                    corpus[stemmed_wrd] = self.corpus_index
                    self.corpus_index += 1
                    # also add a new column in page row and in word_counts
                    info[0].append(1)
                    idf.append(1)
                    for row in word_counts:
                        row.append(0)
                else:  # the word is in the corpus
                    # increment the word count for this word in this page
                    info[0][corpus[stemmed_wrd]] += 1

                    # if this is the first time we've seen this word in this row
                    if info[0][corpus[stemmed_wrd]] == 1:
                        # increment this word's idf n_i count
                        idf[corpus[stemmed_wrd]] += 1

                # update maximum value of this row
                if info[0][corpus[stemmed_wrd]] > info[1]:
                    info[1] = info[0][corpus[stemmed_wrd]]
        

    def make_corpus(self, pages : list):
        """takes in xml pages and populates global variable corpus"""        
       
        id2pn = {}  # page ids to list of names of pages linked to
        max_in_each_row = [] # keeps track of frequency of most frequent word for each page
        ni_counts = [] # keeps track of n_i counts for each word in corpus
        word_counts = []
        weights = [[0 for c in range(len(self.page_ids))] for r in range(len(self.page_ids))]
        corpus = {}

        for page in pages:
            pid = int(page.find('id').text.strip())
            # title = page.find('title').text.strip()
            # self.page_ids.append((pid, title))
            id2pn[pid] = []
            page_row = [0] * len(corpus)
            # two-element list: first element is a list of word counts for the 
            # page, and the second element is the most common word's frequency
            page_info = [page_row, 0]
            num_unique_links = 0
            
            page_words = re.findall(self.n_regex, page.find('title').text + " " + page.find('text').text)

            for word in page_words: # "this", then "is", then "a"....
                if re.match('\[\[[^\[]+?\]\]', word):
                    w = word[2:-2]
                    if '|' in w:
                        link_page, link_text = w.split('|', 1)
                        if link_page in self.title_to_id and self.title_to_id[link_page] not in id2pn[pid] and pid != self.title_to_id[link_page]:
                            weights[self.id_to_index[pid]][self.id_to_index[self.title_to_id[link_page]]] = 0.85
                            num_unique_links += 1
                            id2pn[pid].append(self.title_to_id[link_page])
                        self.add_to_corpus(link_text, page_info, ni_counts, word_counts, corpus)
                    elif ':' in w:
                        if w in self.title_to_id and self.title_to_id[w] not in id2pn[pid] and pid != self.title_to_id[w]:
                            weights[self.id_to_index[pid]][self.id_to_index[self.title_to_id[w]]] = 0.85
                            num_unique_links += 1
                            id2pn[pid].append(self.title_to_id[w])  # we aren't sure if category pages should count as links
                        w = w.replace(":", " ")
                        self.add_to_corpus(w, page_info, ni_counts, word_counts, corpus)
                    else:  # links where the text is the name of the page
                        if w in self.title_to_id and self.title_to_id[w] not in id2pn[pid] and pid != self.title_to_id[w]:
                            weights[self.id_to_index[pid]][self.id_to_index[self.title_to_id[w]]] = 0.85
                            num_unique_links += 1
                            id2pn[pid].append(self.title_to_id[w])
                        self.add_to_corpus(w, page_info, ni_counts, word_counts, corpus)
                else:  # i.e. if the word is not a link
                    self.add_to_corpus(word, page_info, ni_counts, word_counts, corpus)

            word_counts.append(page_info[0])
            max_in_each_row.append(page_info[1])
            if num_unique_links == 0:
                weights[self.id_to_index[pid]] = [0.85/(len(self.page_ids) - 1) + 0.15/len(self.page_ids) for n in weights[self.id_to_index[pid]]]
                weights[self.id_to_index[pid]][self.id_to_index[pid]] = 0.15/len(self.page_ids)
            else:
                weights[self.id_to_index[pid]] = [n/num_unique_links + 0.15/len(self.page_ids) for n in weights[self.id_to_index[pid]]]

                
        # self.calculate_tf(max_in_each_row)
        # self.calculate_idf(idf_arr)

        return IndexInfo(self.calculate_idf(ni_counts), max_in_each_row, word_counts, weights, corpus)

        # could we instead make this function take in the list of pages and 
        # return idf_arr and max_in_each_row and tf_array and id2pn?
        

    # def calculate_tf(self, maxs: list):
    #     for idx, row in enumerate(self.tf_array):
    #         self.tf_array[idx] = [wc / maxs[idx] for wc in row]

    def calculate_idf(self, n_i_list: list) -> list:
        """converts an n_i counts list into an IDF scores list"""
        n = len(self.page_ids)
        return [math.log(n / n_i) for n_i in n_i_list]
    
    # def calculate_relevance(self):
    #     for r in self.tf_array:
    #         self.relevance.append([elem * self.idf_array[idx] for idx, elem in enumerate(r)])

    def make_dicts(self, rel_and_ranks) -> dict:
        """converts relevance array to a dictionary of words to dict(ids, rel)"""
        words_to_relevance = {}
        ids_to_pageranks = {}

        rel_array = rel_and_ranks[0]
        ranks = rel_and_ranks[1]
        corpus = rel_and_ranks[2]

        for col_idx, word in enumerate(corpus.keys()):
            ids_to_relevance = {}
            for row_idx in range(len((rel_array))):
                page_id = self.page_ids[row_idx][0]
                ids_to_relevance[page_id] = rel_array[row_idx][col_idx]

            words_to_relevance[word] = ids_to_relevance

        for i in range(len(self.page_ids)):
            ids_to_pageranks[self.page_ids[i][0]] = ranks[i]

        return words_to_relevance, ids_to_pageranks

    def make_tf_array(self, ii: IndexInfo) -> list:
        """converts an IndexInfo into a term frequency array"""
        tf = [[0 for i in range(len(ii.word_counts[0]))] for j in range(len(ii.word_counts))]
        for idx, row in enumerate(ii.word_counts):
            tf[idx] = [wc / ii.max_per_row[idx] for wc in row]

        return tf

    def distance(self, prev, cur) -> float:
        """euclidean distance between two equally sized arrays of numbers"""
        sum = 0
        for i in range(len(prev)):
            sum += (prev[i] - cur[i])**2

        return math.sqrt(sum)

    def make_scores(self, ii: IndexInfo) -> list:
        """converts an IndexInfo into a relevance scores array"""
        rel = []
        for r in self.make_tf_array(ii):
            rel.append([elem * ii.idf_array[idx] for idx, elem in enumerate(r)])

        cur_ranks = [1/len(self.page_ids) for elem in range(len(self.page_ids))]
        prev_ranks = [0 for elem in range(len(self.page_ids))]
        delta = 0.001

        while self.distance(prev_ranks, cur_ranks) > delta:
            prev_ranks = cur_ranks.copy()
            for j in range(len(self.page_ids)):
                cur_ranks[j] = 0
                for k in range(len(self.page_ids)):
                    cur_ranks[j] += ii.weights[k][j] * prev_ranks[k]

        return rel, cur_ranks, ii.corpus

    def get_pages(self, xml_file: str) -> list:
        """returns the list of pages from a given xml file"""
        root: "Element" = et.parse(xml_file).getroot()
        pages = root.findall("page")
        for index, page in enumerate(pages):
            pid = int(page.find('id').text.strip())
            title = page.find('title').text.strip()
            self.page_ids.append((pid, title))
            self.title_to_id[title] = pid
            self.id_to_index[pid] = index
        return pages

    def reset_variables(self):
        self.page_ids = []  # list of tuples with (page ID, page title)
        self.title_to_id = {} # look up page IDs by title
        self.id_to_index = {}
        self.n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        # self.corpus = {} # keys = words, values = indices
        self.corpus_index = 0  

    def write_files(self, xml_file: str, title_file: str, docs_file: str, words_file: str):
        pages = self.get_pages(xml_file)
        # for index, page in enumerate(pages):
        #     pid = int(page.find('id').text.strip())
        #     title = page.find('title').text.strip()
        #     self.page_ids.append((pid, title))
        #     self.title_to_id[title] = pid
        #     self.id_to_index[pid] = index
        # self.weights = [[0 for c in range(len(self.page_ids))] for r in range(len(self.page_ids))]
       
        wtr_dict, ids_to_pageranks = self.make_dicts(self.make_scores(self.make_corpus(pages)))
        # pass words_to_relevance into file_io to write to words file
        file_io.write_words_file(words_file, wtr_dict)
        # convert page_ids to dictionary and write to title file
        file_io.write_title_file(title_file, dict(self.page_ids))

        file_io.write_docs_file(docs_file, ids_to_pageranks)


if __name__ == "__main__":
    """this should be the "view" of the model view controller"""
    idxr = Indexer(sys.argv[1:])
    print("File successfully indexed!")
