import pytest
from index import *
from query import *
from file_io import *

def test_word_processing():
    """ensure that Indexer adds the words to the corpus that we'd expect"""
    ind = Indexer(["small_test_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])

    expected_corpus = ['juic', 'york', 'blood', 'love', 'mani', 'sport', 
                        'england', 'build', 'popular', 'kitchen', 'peopl', 
                        'billiard', 'tall', 'aluminum', 'live', 'categori', 
                        'use', 'orang', 'citi', 'type', 'commut', 'make', 'nyc',
                        'made', 'new', 'skyscrap', 'foil']
    
    assert len(ind.corpus) == len(expected_corpus)
    for word in expected_corpus:
        assert word in ind.corpus

def test_arguments():
    with pytest.raises(ArgumentError):
        Indexer(["1", "2", "3"])
        Indexer(["1", "2", "3", "4", "5"])

def test_tf():
    """tests that expected term frequencies on a tiny wiki match the code output
    values, and that the linked pages of pipe links are not included in the 
    corpus and not counted in term frequencies."""
    
    expected_corpus = [
        'york', 'mani', 'sport', 
        'england', 'popular', 
        'billiard', 'tall', 'categori', 
        'citi', 'new', 'build'
    ]
    
    ind = Indexer(["pipelink_tiny_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])

    assert len(ind.corpus) == len(expected_corpus)
    for word in expected_corpus:
        assert word in ind.corpus

    expected_tf = [
        [1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    ]
    ind.reset_variables()
    tf_array = ind.make_tf_array(ind.make_corpus(ind.get_pages("pipelink_tiny_wiki.xml"))) 
    assert tf_array == expected_tf
    

def test_idf():
    ind_tiny = Indexer(["pipelink_tiny_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected_idf = [math.log(2)] * 11
    ind_tiny.reset_variables()
    idf_array = ind_tiny.make_corpus(ind_tiny.get_pages("pipelink_tiny_wiki.xml")).idf_array
    assert idf_array == expected_idf

    ind_test_idf = Indexer(["test_idf_wiki.xml", "title_file.txt", "docs_files.txt", "words_file.txt"])
    expected = [math.log(2), math.log(4/3), math.log(2), math.log(2)]
    ind_test_idf.reset_variables()
    idf = ind_test_idf.make_corpus(ind_test_idf.get_pages("test_idf_wiki.xml")).idf_array
    assert idf == expected

def test_relevance():
    ind_test_idf = Indexer(["test_idf_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    expected_rel = [
        [math.log(2), math.log(4/3), 0, 0],
        [0, 0, math.log(2), math.log(2)],
        [0, math.log(4/3), math.log(2)/2, 0],
        [math.log(2)/2, math.log(4/3)/2, 0, math.log(2)]
    ]
    ind_test_idf.reset_variables()
    rel_array = ind_test_idf.make_scores(ind_test_idf.make_corpus(ind_test_idf.get_pages("test_idf_wiki.xml")))[0]
    assert rel_array == expected_rel

def test_querier():
    args = ["test_idf_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"]
    ind_q = Indexer(args)
    querier = Query(args[1:])
    blue_results = querier.retrieve_results(querier.processed_search_terms("blue"))
    assert len(blue_results) == 4
    cat_results = querier.retrieve_results(querier.processed_search_terms("cat"))
    assert len(cat_results) == 0

    args_11 = ["test_wiki_11.xml", "title_file.txt","docs_file.txt", "words_file.txt"]
    ind_11 = Indexer(args_11)
    q11 = Query(args_11[1:])
    # "built" is not in the test wiki, but should return results from stemming
    builds_results = q11.retrieve_results(querier.processed_search_terms("bUiLds"))
    assert len(builds_results) == 10  #even though there are > 10 pages

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
  
    ind_w = Indexer(["test_weights_wiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
    ind_w.reset_variables()
    weights = ind_w.make_corpus(ind_w.get_pages("test_weights_wiki.xml")).weights
    for r in range(4):
        for c in range(4):
            assert weights[r][c] == pytest.approx(expected_weights[r][c])

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
    for i in range(len(expected)):
        assert list(ids_to_pageranks.values())[i] == pytest.approx(expected[i], abs = .0001)

def test_ranks_100():
    ind = Indexer(["PageRankWiki.xml", "title_file.txt", "docs_file.txt", "words_file.txt"])
   
    ids_to_pageranks = {}
    read_docs_file("docs_file.txt", ids_to_pageranks)

    sum = 0
    for rank in ids_to_pageranks.values():
        sum += rank
    assert sum == pytest.approx(1)



