# index.py
from ctypes import ArgumentError
import sys
import re
import math
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import file_io

class WordInfo:
    def __init__(self, unique_page_appearances: int, wrd_cts: dict):
        self.unique_page_appearances = unique_page_appearances
        self.wrd_cts = wrd_cts  # dict of page IDs to word counts

class PageInfo:
    def __init__(self, max_freq: int, links: dict):
        self.max_freq = max_freq
        self.links = links

class Indexer:
    def __init__(self, args):
        if len(args) != 4:
            raise ArgumentError("Must have exactly 4 arguments after index.py -- try again.")
        
        # self.page_ids = []  # list of tuples with (page ID, page title)
        self.title_to_id = {} # look up page IDs by title
        # self.id_to_index = {}
        self.n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        # self.corpus = {} # keys = words, values = indices
        # self.corpus_index = 0  

        self.write_index_files(args[0], args[1], args[2], args[3])

    def process_word(self, pid, word: str, word_info, page_info):
        """returns a stemmed, lower cased word if it's not a stop word, otherwise
        returns False"""
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()

        if word.lower() not in STOP_WORDS:
            w = stemmer.stem(word.lower())
            self.update_corpus(pid, w, word_info, page_info)

    def process_link(self, pid: int, link_page: str, word_info, page_info):
        """stuff"""
        # update link information for link_page, including the page IDs of the from
        # and to pages, weights, number of unique links per page, etc.
        linked_pages = page_info[pid].links
        if link_page in self.title_to_id: # if linked page is in our set of pages
            linked_page_id = self.title_to_id[link_page]
            if linked_page_id not in linked_pages and linked_page_id != pid:
                linked_pages[linked_page_id] = 0.85  # initialize to 1 - E

    def handle_link(self, pid: int, link_string: str, word_info, page_info):
        """identifies link page and link text, and sends link text to be processed
        as words and link text to be processed as links"""
        link_page = link_string
        link_text = link_string
        if '|' in link_string:
            link_page, link_text = link_string.split('|', 1)
        elif ':' in link_string:
             link_text = link_string.replace(":", " ")

        self.process_link(pid, link_page, word_info, page_info)
        for word in re.findall(self.n_regex, link_text):
            self.process_word(pid, word, word_info, page_info)

    def update_corpus(self, pid: int, word: str, word_info, page_info):
        """stuff"""
        word_count = 1 # word count of given word in given page

        if word not in word_info:
            word_info[word] = WordInfo(1, {pid: 1}) # n_i count, dict of ids to word counts
        else: # word is already in corpus
            if pid in word_info[word].wrd_cts: # word has been counted on this page before
                word_info[word].wrd_cts[pid] += 1
                word_count = word_info[word].wrd_cts[pid]
            else: # word has not been counted on this page before
                word_info[word].wrd_cts[pid] = 1
                word_info[word].unique_page_appearances += 1
        
        # update maximum word frequency for the current page, if necessary
        if word_count > page_info[pid].max_freq:
            page_info[pid].max_freq = word_count

    def populate_weights(self, pid: int, page_info: dict):
        linked_pages = page_info[pid].links # dictionary of pages to weights
        if not linked_pages:  # if there are no unique links
            for page in self.title_to_id.values():
                if page != pid:  # record one link to every other page
                    linked_pages[page] = self.calc_link_weight(len(self.title_to_id) - 1, len(self.title_to_id))
        else:
            for page in linked_pages.keys():
                linked_pages[page] = self.calc_link_weight(len(linked_pages), len(self.title_to_id))

    def calc_link_weight(self, num_unique_links: int, num_pages: int) -> float:
        """calculates the weight that a page k gives to a linked page j,
        given k's number of unique links and the total number of pages"""
        ee = 0.15
        return (1 - ee)/num_unique_links + ee/num_pages 

    def process_pages(self, pages: list, word_info, page_info):
        """takes in xml pages, populates word_info with n_i counts and word 
        counts, populates page_info with max term freqs and links/weights"""
        for page in pages:
            pid = int(page.find('id').text.strip())
            page_info[pid] = PageInfo(0, {})  # max word frequency per page, dict of linked page ids to weights

            page_elems = re.findall(self.n_regex, page.find('title').text + " " + page.find('text').text)
            for elem in page_elems:
                if re.match('\[\[[^\[]+?\]\]', elem):
                    self.handle_link(pid, elem[2:-2], word_info, page_info)  # also does link stuff
                else:
                    self.process_word(pid, elem, word_info, page_info)

    def calc_relevance(self, pages, words_to_relevance, page_info):
        """converts the values of word_info from word count numbers into term
        relevance scores by calculating tf and idf scores and multiplying"""
        word_info = {}
        # populates word_info with keys as words, values as WordInfos of (ni counts, dict of ids to word counts)
        self.process_pages(pages, word_info, page_info)

        for word in word_info.keys(): 
            # convert n_i to inverse document frequency scores
            n_i = word_info[word].unique_page_appearances
            idf = math.log(len(self.title_to_id)/n_i)
            # word_info[word][0] = idf
            words_to_relevance[word] = {}  # initialize
            # convert word counts to term frequency scores, calculate relevances
            for pid in word_info[word].wrd_cts.keys():
                wc = word_info[word].wrd_cts[pid]
                tf = wc/page_info[pid].max_freq
                words_to_relevance[word][pid] = tf * idf  

    def euclidean_distance(self, prev: dict, cur: dict):
        """eucli"""
        sum = 0
        for pid in prev.keys():
            sum += (prev[pid] - cur[pid]) * (prev[pid] - cur[pid])
        print(sum)

        return math.sqrt(sum)

    def calc_ranks(self, ids_to_pageranks, page_info):
        """get the pageranks"""
        # cur_ranks = [1/len(self.title_to_id) for i in range(len(self.title_to_id))]
        # prev_ranks = [0 for i in range(len(self.title_to_id))]
        delta = 0.001
        # idx_to_id = {}
        previous_ranks = {}
        for pid in self.title_to_id.values():
            previous_ranks[pid] = 0
            ids_to_pageranks[pid] = 1/len(self.title_to_id)

        print(self.euclidean_distance(previous_ranks, ids_to_pageranks))

        while self.euclidean_distance(previous_ranks, ids_to_pageranks) > delta:
        # for i in range(10):
            previous_ranks = ids_to_pageranks.copy()
            for link_id in self.title_to_id.values():
                ids_to_pageranks[link_id] = 0
                for page_id in self.title_to_id.values():
                    ids_to_pageranks[link_id] += self.calc_weight(page_id, link_id, page_info) * previous_ranks[page_id]
            pass

    def calc_weight(self, pid, link_id, page_info):
        """stuff"""
        linked_pages = page_info[pid].links
        num_unique_links = len(linked_pages)
        ee = 0.15

        if num_unique_links == 0 and pid != link_id:  # pid has no unique links
            return (1 - ee)/(len(self.title_to_id) - 1) + ee/len(self.title_to_id)
        elif link_id in linked_pages:  # pid links to link_id
            return (1 - ee)/num_unique_links + ee/len(self.title_to_id)
        else:   # pid doesn't link to link id
            return ee/len(self.title_to_id)

    def populate_dicts(self, pages, words_to_relevance, ids_to_pageranks):
        """call the methods to be able to populate and return words_to_relevance
        and ids_to_pageranks"""

        # once populated, page_info has page IDs as keys and PageInfos of 
        # (max freq, dict of linked IDs to weights) as values
        page_info = {}

        # populates words_to_relevance and page info
        self.calc_relevance(pages, words_to_relevance, page_info)
        # populates ids_to_pageranks (needs page_info to be already populated)
        self.calc_ranks(ids_to_pageranks, page_info)

    def write_index_files(self, xml_file: str, title_file: str, docs_file: str, words_file: str):
        pages, ids_to_titles = self.get_pages(xml_file)
       
        words_to_relevance = {}
        ids_to_pageranks = {}
        self.populate_dicts(pages, words_to_relevance, ids_to_pageranks)

        file_io.write_words_file(words_file, words_to_relevance)
        file_io.write_title_file(title_file, ids_to_titles)
        file_io.write_docs_file(docs_file, ids_to_pageranks)

    def get_pages(self, xml_file: str) -> list:
        """returns the list of pages from a given xml file, and a dict of page
        IDs to page titles"""
        root: "Element" = et.parse(xml_file).getroot()
        pages = root.findall("page")
        ids_to_titles = {}
        for index, page in enumerate(pages):
            pid = int(page.find('id').text.strip())
            title = page.find('title').text.strip()
            ids_to_titles[pid] = title
            self.title_to_id[title] = pid
            # self.id_to_index[pid] = index
        return pages, ids_to_titles

if __name__ == "__main__":
    """this should be the "view" of the model view controller"""
    idxr = Indexer(sys.argv[1:])
    print("File successfully indexed!")