import pytest
from index import *
from query import *
from file_io import *
import xml.etree.ElementTree as et

# many of the test methods use a common set of arguments
txt_args = ["title_file.txt", "docs_file.txt", "words_file.txt"]

def test_word_processing():
    """
    Tests that the indexer correctly stems and removes stop words when adding 
    to the corpus for a small test wiki for which we know the expected values.
    """
    args = ["small_test_wiki.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    word_info = ind.process_pages(ind.get_pages(args[0])[0])[0]

    expected_corpus = ['juic', 'york', 'blood', 'love', 'mani', 'sport', 
                        'england', 'build', 'popular', 'kitchen', 'peopl', 
                        'billiard', 'tall', 'aluminum', 'live', 'categori', 
                        'use', 'orang', 'citi', 'type', 'commut', 'make', 'nyc',
                        'made', 'new', 'skyscrap', 'foil']
    
    assert len(word_info) == len(expected_corpus)
    for word in expected_corpus:
        assert word in word_info

def test_arguments():
    """
    Tests that Indexer raises appropriate exceptions (ArgumentErrors and 
    FileNotFoundErrors) for misspelled, missing, or extra arguments.  These 
    exceptions are all handled in the main method and informative messages are 
    printed, but for this test class which doesn't run the indexer main method, 
    we just test that the exceptions are thrown.
    """
    with pytest.raises(ArgumentError):
        Indexer(["1", "2", "3"]) # must have 4 arguments
        Indexer(["1", "2", "3", "4", "5"]) # must have 4 arguments
        Query(["1", "2"]) # must have 3 or 4 arguments
        Query(["1", "2", "3", "4", "5"]) # must have 3 or 4 arguments
        Query(["1", "2", "3", "4"]) # if 4 arguments, first must be --pagerank

        # the first argument must end in .xml
        Indexer(["index.py", "title_file.txt", "doc_file.txt", "word_file.txt"])

        # the latter 3 arguments must end in .txt
        Indexer(["MedWiki.xml", "title_file.txt", "docs_file.txt", "gitignore"])

    with pytest.raises(FileNotFoundError):  # only if the xml file isn't found
        Indexer(["p.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
        Query(["title_file.txt", "docs_file.txt", "3"])
        Query(["--pagerank", "title_file.txt", "docs_file.txt", "3"])
        Query(["--pagerank", "title_file.txt", "docs_file.txt"])


def test_empty_wiki():
    """
    Tests that the indexer and querier can handle XML pages where either the 
    title or the text of a page could be empty.
    """
    args = ["empty_wiki.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    querier = Query(txt_args)

    empty_results = querier.retrieve_results(querier.processed_terms(""))
    assert len(empty_results) == 0  # should have no results for empty string

    any_results = querier.retrieve_results(querier.processed_terms("cat"))
    assert len(any_results) == 0  # should have no results for any string

def test_relevance1():
    """
    Tests that term relevance scores match expected values for a small wiki on
    which several types of links and varying term frequencies are included.
    """
    args = ["test_idf_wiki.xml"]
    args.extend(txt_args)
    ind_test_idf = Indexer(args)
    expected_wtr = {
        'orang': {1: math.log(2), 4: math.log(2)/2},
        'peopl': {1: math.log(4/3), 3: math.log(4/3), 4: math.log(4/3)/2},
        'citi': {2: math.log(2), 3: math.log(2)/2},
        'blue': {2: math.log(2), 4: math.log(2)}
    }
    # calculating words_to_relevance dict 
    pages = ind_test_idf.get_pages(args[0])[0]
    words_to_relevance = ind_test_idf.calc_relevance(pages)[0]

    for word in expected_wtr.keys():
        for pid in expected_wtr[word].keys():
                assert words_to_relevance[word][pid] == expected_wtr[word][pid]

def test_revelance2():
    """
    Tests a slightly larger wiki with every type of link, including where the 
    address of the link page should not be included in the word count.
    """
    args = ["test_rel_wiki.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    expected_wtr = {
        # orange appears in multiple documents in high numbers
       'orang': {1: math.log(5/3), 3: math.log(5/3), 4: math.log(5/3)},
       'mani': {1: .5*math.log(5/2), 2: math.log(5/2)},
       'peopl': {1: .5*math.log(5)},
       'make': {1: .5*math.log(5)},
       'juic': {1: .5*math.log(5)},
       'new': {2: math.log(5)},
       'york': {2: math.log(5)},
       'citi': {2: math.log(5)},
       'nyc': {2: math.log(5/2), 5: math.log(5/2)},
       'build': {2: math.log(5/2), 5: math.log(5/2)},
       'blood': {3: (1/2)*math.log(5)}, 
       'aluminum': {4: math.log(5)},
       'categori': {5: math.log(5)}
    }
    # calculating words_to_relevance dict 
    words_to_relevance = ind.calc_relevance(ind.get_pages(args[0])[0])[0]

    for word in expected_wtr.keys():
        for pid in expected_wtr[word].keys():
            assert words_to_relevance[word][pid] == expected_wtr[word][pid]

def test_querier():
    """
    Tests that query.py returns expected results in different scenarios, 
    including fewer than 10 results, no results (for words not in the wiki, stop
    words, and empty strings), and more than 10 possible results (in which case 
    only 10 should be returned).
    """
    args = ["test_wiki_11.xml"]
    args.extend(txt_args)
    ind_q = Indexer(args)
    querier = Query(txt_args)

    orange_results = querier.retrieve_results(querier.processed_terms("orange"))
    # there are 4 pages in this wiki, but only City and Blue have the word blue
    assert len(orange_results) == 2  
    assert "Oranges" in orange_results
    assert "Blood Oranges" in orange_results

    cart_results = querier.retrieve_results(querier.processed_terms("cart"))
    assert len(cart_results) == 0  # no pages have the word cart

    empty_results = querier.retrieve_results(querier.processed_terms(""))
    assert len(empty_results) == 0  # should have no results for empty string

    stopword_results = querier.retrieve_results(querier.processed_terms("in"))
    # should have no results for a stop word, even though it's in the wiki text
    assert len(stopword_results) == 0  

    builds_results = querier.retrieve_results(querier.processed_terms("bUiLds"))
    # number of results should be 10 even though > 10 pages have this word
    assert len(builds_results) == 10  

def test_weights():
    """
    Tests that pagerank weights are appropriately calculated for various kinds
    of pages: ones with no links at all, only links to outside corpus, and with
    different numbers of in-corpus links.
    """
    expected_weights = [
        [.0375, .0375 + 0.85/3, .0375 + 0.85/3, .0375 + 0.85/3],
        [.0375 + 0.85/3, .0375, .0375 + 0.85/3, .0375 + 0.85/3],
        [.4625, .4625, .0375, .0375],
        [.0375, .0375, .8875, .0375]
    ]
    args = ["test_weights_wiki.xml"]
    args.extend(txt_args)
    ind_w = Indexer(args)
    page_info = {}
    page_info = ind_w.calc_relevance(ind_w.get_pages(args[0])[0])[1]
    for r in range(4):
        for c in range(4):
            print(str(r) + " " + str(c))
            print(ind_w.num_pages)
            print(page_info)
            assert ind_w.calc_weight(r+1, c+1, page_info[r+1].links) \
                == pytest.approx(expected_weights[r][c])

def test_ranks_ex1():
    """
    Tests that PageRank scores match expected values for the first example wiki,
    where first page has two links, 2nd has no links, and 3rd has pipe link
    """
    args = ["PageRankExample1.xml"]
    args.extend(txt_args)
    ind = Indexer(args)  # populates docs_file.txt with this wiki's scores

    expected = [0.4326,0.2340,0.3333]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(3):
        assert list(ids_to_pageranks.values())[i] \
            == pytest.approx(expected[i], abs = .0001)

def test_ranks_ex2():
    """
    Tests that PageRank scores match expected values for the second example wiki
    where multiple pages have two links going to them, but D should be ranked
    higher than C because the pages that link to D have fewer links on them.
    """
    args = ["PageRankExample2.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    expected = [0.2018, 0.0375, 0.3740, 0.3867]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(len(expected)):
        assert list(ids_to_pageranks.values())[i] \
            == pytest.approx(expected[i], abs = .0001)

def test_ranks_ex3():
    """
    Tests that PageRank scores match expected values for the third example wiki,
    which includes links from a page to itself in both regular and pipe form.
    """
    args = ["PageRankExample3.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    expected = [0.0524, 0.0524, 0.4476, 0.4476]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(len(expected)):
        assert list(ids_to_pageranks.values())[i] \
            == pytest.approx(expected[i], abs = .0001)

def test_ranks_ex4():
    """
    Tests that PageRank scores match expected values for the fourth example wiki
    where one page has multiple links to another page (which should be treated
    as just one link to that page).
    """
    args = ["PageRankExample4.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
    expected = [0.0375, 0.0375, 0.4625, 0.4625]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    sum = 0
    for i in range(len(expected)):
        sum += list(ids_to_pageranks.values())[i]
        assert list(ids_to_pageranks.values())[i] == \
            pytest.approx(expected[i], abs = .0001)
    assert sum == pytest.approx(1) # testing the sum of pagerank scores equals 1

def test_ranks_100():
    """
    Tests that PageRank scores add up to 1 for an example where 100 pages all 
    link to the hundredth page.
    """
    args = ["PageRankWiki.xml"]
    args.extend(txt_args)
    ind = Indexer(args)
   
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)

    sum = 0
    for rank in ids_to_pageranks.values():
        sum += rank
    assert sum == pytest.approx(1) # testing the sum of pagerank scores equals 1