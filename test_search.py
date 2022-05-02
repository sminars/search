import pytest
from index import *
from query import *
from file_io import *

def test_word_processing():
    """ensure that Indexer adds the words to the corpus that we'd expect"""
    args = ["small_test_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
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
    with pytest.raises(ArgumentError):
        Indexer(["1", "2", "3"])
        Indexer(["1", "2", "3", "4", "5"])

def test_relevance1():
    args = ["test_idf_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
    ind_test_idf = Indexer(args)
    expected_wtr = {
        'orang': {1: math.log(2), 4: math.log(2)/2},
        'peopl': {1: math.log(4/3), 3: math.log(4/3), 4: math.log(4/3)/2},
        'citi': {2: math.log(2), 3: math.log(2)/2},
        'blue': {2: math.log(2), 4: math.log(2)}
    }
    # calculating words_to_relevance dict 
    words_to_relevance = ind_test_idf.calc_relevance(ind_test_idf.get_pages(args[0])[0])[0]

    for word in expected_wtr.keys():
        for pid in expected_wtr[word].keys():
                assert words_to_relevance[word][pid] == expected_wtr[word][pid]

def test_revelance2():
    # testing a slightly larger wiki with every type of link, address of link page is not included in word count 
    args = ["test_rel_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
    ind = Indexer(args)
    expected_wtr = {
       'orang': {1: math.log(5/3), 3: math.log(5/3), 4: math.log(5/3)}, # orange appears in multiple documents in high numbers
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
    args = ["test_idf_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
    ind_q = Indexer(args)
    querier = Query(args[1:])
    blue_results = querier.retrieve_results(querier.processed_search_terms("blue"))
    assert len(blue_results) == 2  # there are 4 pages in this wiki, but only two pages have the word blue
    cat_results = querier.retrieve_results(querier.processed_search_terms("cat"))
    assert len(cat_results) == 0  # no pages have the word cat

    args_11 = ["test_wiki_11.xml", "title_file.txt","docs_file.txt", "words_file.txt"]
    ind_11 = Indexer(args_11)
    q11 = Query(args_11[1:])
    builds_results = q11.retrieve_results(querier.processed_search_terms("bUiLds"))
    assert len(builds_results) == 10  #even though there are > 10 pages with this stemmed word

def test_weights():
    """test that pagerank weights are appropriately calculated for various kinds
    of pages: ones with no links at all, only links to outside corpus, and with
    different numbers of in-corpus links"""
    expected_weights = [
        [.0375, .0375 + 0.85/3, .0375 + 0.85/3, .0375 + 0.85/3],
        [.0375 + 0.85/3, .0375, .0375 + 0.85/3, .0375 + 0.85/3],
        [.4625, .4625, .0375, .0375],
        [.0375, .0375, .8875, .0375]
    ]
    args = ["test_weights_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
    ind_w = Indexer(args)
    page_info = {}
    page_info = ind_w.calc_relevance(ind_w.get_pages(args[0])[0])[1]
    for r in range(4):
        for c in range(4):
            print(str(r) + " " + str(c))
            print(ind_w.num_pages)
            print(page_info)
            assert ind_w.calc_weight(r+1, c+1, page_info[r+1].links) == pytest.approx(expected_weights[r][c])

def test_ranks_ex1():
    """tests a wiki where first page has 2 links, second page has no links, and third page has pipe link"""
    ind = Indexer(["PageRankExample1.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected = [0.4326,0.2340,0.3333]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(3):
        assert list(ids_to_pageranks.values())[i] == pytest.approx(expected[i], abs = .0001)

def test_ranks_ex2():
    """tests pagerank example 2 wiki"""
    ind = Indexer(["PageRankExample2.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected = [0.2018, 0.0375, 0.3740, 0.3867]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(len(expected)):
        assert list(ids_to_pageranks.values())[i] == pytest.approx(expected[i], abs = .0001)

def test_ranks_ex3():
    """tests pagerank example 3 wiki"""
    ind = Indexer(["PageRankExample3.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected = [0.0524, 0.0524, 0.4476, 0.4476]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    for i in range(len(expected)):
        assert list(ids_to_pageranks.values())[i] == pytest.approx(expected[i], abs = .0001)
   

def test_ranks_ex4():
    """tests pagerank example 4 wiki"""
    ind = Indexer(["PageRankExample4.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected = [0.0375, 0.0375, 0.4625, 0.4625]
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)
    sum = 0
    for i in range(len(expected)):
        sum += list(ids_to_pageranks.values())[i]
        assert list(ids_to_pageranks.values())[i] == pytest.approx(expected[i], abs = .0001)
    assert sum == pytest.approx(1) # testing the sum of pagerank scores equals 1

def test_ranks_100():
    ind = Indexer(["PageRankWiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
   
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)

    sum = 0
    for rank in ids_to_pageranks.values():
        sum += rank
    assert sum == pytest.approx(1) # testing the sum of pagerank scores equals 1



