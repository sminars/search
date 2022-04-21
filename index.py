# index.py
import sys
import re
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class Indexer:
    def __init__(self, args):
        if len(args) != 4:
            print("Must have exactly 4 arguments after index.py -- try again.")
            sys.exit()
    
        root: "Element" = et.parse(args[0]).getroot()
        all_pages: "ElementTree" = root.findall("page")
        self.corpus = set()
        self.make_corpus(all_pages)

    def add_to_corpus(self, words: str):
        """tokenizes, lower cases, and stems the elements of words and adds non-
        stop words to self.corpus"""
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''

        tokens = re.findall(n_regex, words)
        for wrd in tokens:
            if wrd.lower() not in STOP_WORDS:
                self.corpus.add(stemmer.stem(wrd.lower()))


    def make_corpus(self, pages : list):
        """takes in xml pages and populates global variable corpus"""        
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        ids = []
        id2pn = {}  # page ids to list of names of pages linked to
        
        for page in pages:
            pid = int(page.find('id').text.strip())
            ids.append(pid)
            id2pn[pid] = []

            page_words = re.findall(n_regex, page.find('title').text + " " + page.find('text').text)

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
                elif word.lower() not in STOP_WORDS:
                    self.corpus.add(stemmer.stem(word.lower()))

        print(id2pn)
        print(ids)
        print("the" in STOP_WORDS)
        print(self.corpus)

if __name__ == "__main__":
    idxr = Indexer(sys.argv[1:])
