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
        self.make_corpus(self.all_pages)
       
       
      

    def add_to_corpus(self, words: str):
        """tokenizes, lower cases, and stems the elements of words and adds non-
        stop words to self.corpus"""
        tokens = re.findall(self.n_regex, words)
        for wrd in tokens:
            if wrd.lower() not in self.STOP_WORDS:
                stemmed_wrd = self.stemmer.stem(wrd.lower())
                if stemmed_wrd not in self.corpus:
                    self.corpus[stemmed_wrd] = self.index
                    self.index += 1
        

    def make_corpus(self, pages : list):
        """takes in xml pages and populates global variable corpus"""        
       
        ids = []
        id2pn = {}  # page ids to list of names of pages linked to

        word_counts = []
        for page in pages:
            pid = int(page.find('id').text.strip())
            ids.append(pid)
            id2pn[pid] = []
            page_row = []
            
            page_words = re.findall(self.n_regex, page.find('title').text + " " + page.find('text').text)

            for word in page_words: # "this", then "is", then "a"....
                if re.match('\[\[[^\[]+?\]\]', word):
                    w = word[2:-2]
                    if '|' in w:
                        link_page, link_text = w.split('|')
                        id2pn[pid].append(link_page.lower())
                        self.add_to_corpus(link_text)
                    elif ':' in w:
                        id2pn[pid].append(w)
                        w = w.replace(":", " ")
                        self.add_to_corpus(w)
                    else:  # links where the text is the name of the page
                        id2pn[pid].append(w)
                        self.add_to_corpus(w)
                # elif word.lower() not in STOP_WORDS:
                #     self.corpus.add(stemmer.stem(word.lower()))
                else:
                    self.add_to_corpus(word)
                

       # print(id2pn)
      #  print(ids)
        # print("the" in STOP_WORDS)
        #print(self.corpus)
        #self.calculate_tf(id2pn)

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
   
