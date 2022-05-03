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
    """
    Objects of this class store information about words in a corpus, namely the
    number of unique page appearances a word makes in a corpus and a dictionary
    keyed on the page IDs the word appears in, with word counts as values.
    """
    def __init__(self, unique_page_appearances: int, wrd_cts: dict):
        self.unique_page_appearances = unique_page_appearances
        self.wrd_cts = wrd_cts  # dict of page IDs to word counts

class PageInfo:
    """
    Objects of this class store information about pages in a corpus, namely the
    frequency of the most frequent word in a given page and a set of the page 
    IDs of any pages that the page links to.
    """
    def __init__(self, max_freq: int, links: set):
        self.max_freq = max_freq
        self.links = links

class Indexer:
    """
    Objects of this class take in an XML file of wiki pages containing tagged
    titles, page IDs, and text with various kinds of links in [[]] notation, 
    calculates term relevance and PageRank scores, and stores that information 
    in text files to enable rapid searching with or without PageRank applied.
    """
    def __init__(self, args: list):
        if len(args) != 4:
            raise ArgumentError
        if len(args[0]) < 4 or args[0][-4:] != '.xml':
            raise ArgumentError
        for arg in args[1:]:
            if len(arg) < 4 or arg[-4:] != '.txt':
                raise ArgumentError
        
        self.title_to_id = {} # look up page IDs by title
        self.num_pages = 0  # keep track of number of pages in corpus
        self.n_regex = \
            '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''

        self.write_index_files(args[0], args[1], args[2], args[3])

    def write_index_files(self, xml_file: str, title_file: str, docs_file: str, 
    words_file: str):
        """
        Calls methods to index a given corpus of wiki pages into a set of
        dictionaries, and then writes each of those dictionaries to a given
        text file using methods from file_io.

        Parameters:
        xml_file -- filepath string of an XML-format corpus of wiki pages
        title_file -- filepath string for storing page IDs and titles
        docs_file -- filepath string for storing page IDs and PageRank scores
        words_file -- filepath string for storing words & term relevance scores
        """
        # populates ids_to_titles and counts/records pages in the corpus
        pages, ids_to_titles = self.get_pages(xml_file)
        # populates words_to_relevance & records info about links in page_info
        words_to_relevance, page_info = self.calc_relevance(pages)
        # populates ids_to_pageranks using the now-populated page_info
        ids_to_pageranks = self.calc_ranks(page_info)

        file_io.write_words_file(words_file, words_to_relevance)
        file_io.write_title_file(title_file, ids_to_titles)
        file_io.write_docs_file(docs_file, ids_to_pageranks)

    def get_pages(self, xml_file: str) -> tuple("list, dict"):
        """
        Uses xml ElementTree library to scan through the an XML file's pages,
        counting them and creating lookup tables for their titles and IDs.
        
        Parameters:
        xml_file -- filepath string of an XML-format corpus of wiki pages
        
        Returns:
        pages -- a list of parsed XML pages
        ids_to_titles -- a hashtable with page IDs as keys and titles as values
        
        Populates global variables:
        self.title_to_id -- hashtable with page titles as keys and IDs as values
        self.num_pages -- the number of pages in the corpus
        """
        root: "Element" = et.parse(xml_file).getroot()
        pages = root.findall("page")
        ids_to_titles = {}
        self.num_pages = 0
        for page in pages:
            pid = int(page.find('id').text.strip())
            title = page.find('title').text.strip()
            ids_to_titles[pid] = title
            self.title_to_id[title] = pid
            self.num_pages += 1
        return pages, ids_to_titles

    def calc_ranks(self, page_info: dict):
        """
        Calculates PageRank scores for the pages in the corpus using a while
        loop that recalculates PageRank scores based on the weights that pages
        give one another) until the scores converge below a threshold.
        
        Parameters:
        page_info -- a dict keyed on page IDs containing sets of linked pages

        Returns:
        ids_to_pageranks -- a dict of page IDs to PageRank scores
        """
        delta = 0.001
        previous_ranks = {}
        ids_to_pageranks = {}
        for pid in self.title_to_id.values():
            previous_ranks[pid] = 0
            ids_to_pageranks[pid] = 1/self.num_pages

        while self.euclidean_distance(previous_ranks, ids_to_pageranks) > delta:
            previous_ranks = ids_to_pageranks.copy()
            for link_id in self.title_to_id.values():
                ids_to_pageranks[link_id] = 0
                for pid in self.title_to_id.values():
                    wkj = self.calc_weight(pid, link_id, page_info[pid].links)
                    ids_to_pageranks[link_id] += wkj * previous_ranks[pid]

        return ids_to_pageranks

    def calc_weight(self, pid: int, other_id, linked_pages: set) -> float:
        """
        Given a page and a set of that page's linked pages, determines the 
        weight that page gives to another page in a PageRank scheme.
        
        Parameters:
        pid -- integer page ID of the given page
        other_id -- integer page ID of the page to which pid gives weight
        linked_pages -- the set of page IDs to which pid links
        
        Returns:
        a float representing the weight that pid gives to other_id"""
        num_links = len(linked_pages)
        ee = 0.15

        if num_links == 0 and pid != other_id:  # pid has no unique links
            return (1 - ee)/(self.num_pages - 1) + ee/self.num_pages
        elif other_id in linked_pages:  # pid links to link_id
            return (1 - ee)/num_links + ee/self.num_pages
        else:   # pid doesn't link to link id or pid == link_id
            return ee/self.num_pages

    def euclidean_distance(self, prev: dict, cur: dict):
        """
        Given two equally sized dictionaries keyed on page IDs, returns the 
        Euclidean distance (square root of sum of squared differences) between
        the two sets of values.
        
        Parameters:
        prev -- dict mapping page ID keys to pagerank score values (previous)
        cur -- dict mapping page ID keys to pagerank score values (current)

        Returns:
        the Euclidean distance between the previous and current set of pageranks
        """
        sum = 0
        for pid in prev.keys():
            sum += (prev[pid] - cur[pid]) * (prev[pid] - cur[pid])

        return math.sqrt(sum)

    def calc_relevance(self, pages):
        """
        Calls method to compute word counts, count links, and keep track of per-
        page max frequencies and per-word document appearance counts, then uses
        that information to compute term relevance scores.
        
        Parameters:
        pages -- list of XML pages in the corpus
        
        Returns:
        words_to_relevance -- dict of words as keys, dicts of page IDs to term
        relevance scores as values
        page_info -- dict keyed on page IDs with PageInfos as values (which keep
        track of sets of linked pages and per-page maximum word frequencies)
        """
        words_to_relevance = {}

        # must scan all words and all pages before we can calculate relevances        
        word_info, page_info = self.process_pages(pages)

        for word in word_info.keys(): 
            # convert n_i to inverse document frequency scores
            n_i = word_info[word].unique_page_appearances
            idf = math.log(self.num_pages/n_i)

            words_to_relevance[word] = {}  # initialize
            # convert word counts to term frequency scores, compute relevances
            for pid in word_info[word].wrd_cts.keys():
                wc = word_info[word].wrd_cts[pid]
                tf = wc/page_info[pid].max_freq
                words_to_relevance[word][pid] = tf * idf  

        return words_to_relevance, page_info

    def process_pages(self, pages: list):
        """
        Given a list of XML pages in a corpus, populates word_info with word
        counts and n_i counts (# of documents each word appears in), and 
        populates page_info with maximum word frequencies and sets of linked
        pages, using separate helper methods for regular words vs links.
        
        Parameters:
        pages -- list of XML pages in the corpus
        
        Returns:
        word_info -- dict keyed on words with WordInfos as values (which keep
        track of #s of documents each word appears in, and per-page word counts)
        page_info -- dict keyed on page IDs with PageInfos as values (which keep
        track of sets of linked pages and per-page maximum word frequencies)
        """
        word_info = {}
        page_info = {}

        for page in pages:
            pid = int(page.find('id').text.strip())
            p_info = PageInfo(0, set())  
            page_info[pid] = p_info

            page_elems = []
            pg_title = page.find('title').text
            pg_text = page.find('text').text
            if pg_title and pg_text:  # avoids empty titles or empty texts
                page_elems = re.findall(self.n_regex, pg_title + " " + pg_text)
            for elem in page_elems:
                if re.match('\[\[[^\[]+?\]\]', elem):  # if elem is a link
                    self.handle_link(pid, elem[2:-2], word_info, p_info)
                else:
                    self.process_word(pid, elem, word_info, p_info)

        return word_info, page_info

    def handle_link(self, pid: int, link_str: str, word_info, p_info: PageInfo):
        """
        Parses the interior of a link into its components (link page and link 
        text), and sends those components into appropriate helper methods to be
        indexed.  Supports pipe links, colon links, and regular links. 
        as words and link text to be processed as links.
        
        Parameters:
        pid -- integer page ID of the given page
        word_info -- dict keyed on words with WordInfos as values (which keep
        track of #s of documents each word appears in, and per-page word counts)
        p_info -- PageInfo object keeping track of the maximum word frequency 
        and the set of linked pages for the given page
        """
        link_page = link_str
        link_text = link_str
        if '|' in link_str:
            link_page, link_text = link_str.split('|', 1)
        elif ':' in link_str:
             link_text = link_str.replace(":", " ")

        self.process_link(pid, link_page, p_info.links)
        for word in re.findall(self.n_regex, link_text):
            self.process_word(pid, word, word_info, p_info)

    def process_link(self, pid: int, link_page: str, linked_pages: set):
        """
        Adds a given link page ID to the set of linked pages for a given page
        if the link page is in the corpus, isn't already in the set of linked
        pages, and doesn't match the page ID of the given page.

        Parameters:
        pid -- integer page ID of the given page
        link_page -- string title of a page that is linked in the given page
        linked_pages -- the set of pages to which the given page already links
        """
        if link_page in self.title_to_id: 
            linked_page_id = self.title_to_id[link_page]
            if linked_page_id not in linked_pages and linked_page_id != pid:
                linked_pages.add(linked_page_id)

    def process_word(self, pid: int, w: str, word_info: dict, p_info: PageInfo):
        """
        Calls other methods to register the presence of a word on a given page, 
        either by adding a new entry into the corpus or updating an existing 
        entry, first checking if the word is a valid stemmable non-stop word.

        Parameters:
        pid -- integer page ID of the given page
        w -- string of a single word in the corpus to be potentially counted
        word_info -- dict keyed on words with WordInfos as values (which keep
        track of #s of documents each word appears in, and per-page word counts)
        p_info -- PageInfo object keeping track of the maximum word frequency 
        and the set of linked pages for the given page
        """
        wrd = self.stemmed(w)
        if wrd:
            count = 1
            if wrd not in word_info:  # then add an entry for it into corpus
                word_info[wrd] = word_info[wrd] = WordInfo(1, {pid: 1})
            else:
                self.update_corpus(pid, word_info[wrd])
                count = word_info[wrd].wrd_cts[pid]
            self.update_max_freq(count, p_info)

    def stemmed(self, word: str):
        """
        Returns a stemmed, lower-cased version of a word to update the corpus if
        it's not a stop word according to the nltk library.

        Parameters:
        word -- a string word in the corpus

        Returns:
        a stemmed lower-cased version of the word if it's not a stop word, or 
        False otherwise
        """
        STOP_WORDS = set(stopwords.words('english'))
        stemmer = PorterStemmer()

        if word.lower() not in STOP_WORDS:
            return stemmer.stem(word.lower())
        else:
            return False

    def update_max_freq(self, count: int, p_info: PageInfo):
        """
        Updates a PageInfo's maximum word frequency if the word count of a given
        word on that page exceeds the currently recorded maximum.

        Parameters:
        count -- integer number of times a word has appeared on a page
        p_info -- PageInfo object keeping track of the maximum word frequency 
        and the set of linked pages for the given page
        """
        if count > p_info.max_freq:
            p_info.max_freq = count

    def update_corpus(self, pid: int, w_info: WordInfo):
        """
        Records the presence of a valid stemmed word on a given page ID that's 
        already in the corpus, but not necessarily counted on the given page.

        Parameters:
        pid -- integer page ID of the given page
        w_info -- a WordInfo object keeping track of the number of documents 
        a given word appears in, as well as its per-page word counts
        """
        if pid in w_info.wrd_cts: # word has been counted on this page before
            w_info.wrd_cts[pid] += 1
        else: # word has not been counted on this page before
            w_info.wrd_cts[pid] = 1
            w_info.unique_page_appearances += 1

if __name__ == "__main__":
    """
    Passes command-line arguments into Indexer constructor and catches errors.
    """
    try:
        idxr = Indexer(sys.argv[1:])
        print("File successfully indexed!")
    except ArgumentError:
        print("Try again. Must include the following 4 arguments: \n<pages-file"
            + ">.xml <title-file>.txt <docs-file>.txt <words-file>.txt")
    except FileNotFoundError:
        print(sys.argv[1] + " not found. Try again.")