# index.py
from ctypes import ArgumentError
import sys
import re
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class Indexer:
    def __init__(self, args):
        if len(args) != 4:
            raise ArgumentError("Must have exactly 4 arguments after index.py -- try again.")
    
        root: "Element" = et.parse(args[0]).getroot()
        self.all_pages: "ElementTree" = root.findall("page")
        self.n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        self.STOP_WORDS = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.corpus = {} # keys = words, values = indices
        self.index = 0
        self.word_counts = []
        self.make_corpus(self.all_pages)
       
       
      

    def add_to_corpus(self, words: str, info):
        """tokenizes, lower cases, and stems the elements of words and adds non-
        stop words to self.corpus"""
        tokens = re.findall(self.n_regex, words)
        for wrd in tokens:
            if wrd.lower() not in self.STOP_WORDS:
                stemmed_wrd = self.stemmer.stem(wrd.lower())
                if stemmed_wrd not in self.corpus:
                    self.corpus[stemmed_wrd] = self.index
                    self.index += 1
                    # also add a new column in page row and in word_counts
                    info[0].append(1)
                    for row in self.word_counts:
                        row.append(0)
                else:
                    info[0][self.corpus[stemmed_wrd]] += 1
                    # update maximum value of this row
                if info[0][self.corpus[stemmed_wrd]] > info[1]:
                    info[1] = info[0][self.corpus[stemmed_wrd]]
        

    def make_corpus(self, pages : list):
        """takes in xml pages and populates global variable corpus"""        
       
        ids = []
        id2pn = {}  # page ids to list of names of pages linked to
        max_in_each_row = []

        for page in pages:
            pid = int(page.find('id').text.strip())
            ids.append(pid)
            id2pn[pid] = []
            page_row = [0] * len(self.corpus)
            current_row_max = 0
            page_info = [page_row, current_row_max]
            
            page_words = re.findall(self.n_regex, page.find('title').text + " " + page.find('text').text)

            for word in page_words: # "this", then "is", then "a"....
                if re.match('\[\[[^\[]+?\]\]', word):
                    w = word[2:-2]
                    if '|' in w:
                        link_page, link_text = w.split('|')
                        id2pn[pid].append(link_page.lower())
                        self.add_to_corpus(link_text, page_info)
                    elif ':' in w:
                        id2pn[pid].append(w)
                        w = w.replace(":", " ")
                        self.add_to_corpus(w, page_info)
                    else:  # links where the text is the name of the page
                        id2pn[pid].append(w)
                        self.add_to_corpus(w, page_info)
                # elif word.lower() not in STOP_WORDS:
                #     self.corpus.add(stemmer.stem(word.lower()))
                else:
                    self.add_to_corpus(word, page_info)

            self.word_counts.append(page_info[0])
            max_in_each_row.append(page_info[1])
                

       # print(id2pn)
      #  print(ids)
        # print("the" in STOP_WORDS)
        #print(self.corpus)
        #self.calculate_tf(id2pn)
        for row in self.word_counts:
            print(row)
        print(max_in_each_row)

    def calculate_tf(self, pages : dict):

      
        numRows = len(pages)
        numCols = len(self.corpus)
        tf_array = [[0 for i in range(numCols)] for j in range(numRows)]

        for r, pg in enumerate(self.all_pages):
            page_words = re.findall(self.n_regex, pg.find('title').text + " " + pg.find('text').text)
            for wrd in page_words:
                if wrd.lower() not in self.STOP_WORDS:
                    stemmed_wrd = self.stemmer.stem(wrd.lower())
                    tf_array[r][self.corpus[stemmed_wrd]] += 1

        
        for row in range(numRows):
            print(tf_array[row])


if __name__ == "__main__":
    idxr = Indexer(sys.argv[1:])
   
