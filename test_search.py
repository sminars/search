import pytest
from index import *
from query import *

def test_word_processing():
    """ensure that Indexer adds the words to the corpus that we'd expect"""
    ind = Indexer(["small_test_wiki.xml", "title_file.txt", "", "words_file.txt"])

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
    
    ind = Indexer(["pipelink_tiny_wiki.xml", "title_file.txt", "", "words_file.txt"])

    assert len(ind.corpus) == len(expected_corpus)
    for word in expected_corpus:
        assert word in ind.corpus

    expected_tf = [
        [1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    ]

   

    assert ind.tf_array == expected_tf
    

def test_idf():
    ind_tiny = Indexer(["pipelink_tiny_wiki.xml", "title_file.txt", "", "words_file.txt"])
    expected_idf = [math.log(2)] * 11
    assert ind_tiny.idf_array == expected_idf

    ind_test_idf = Indexer(["test_idf_wiki.xml", "title_file.txt", "", "words_file.txt"])
    expected = [math.log(2), math.log(4/3), math.log(2), math.log(2)]
    assert ind_test_idf.idf_array == expected

def test_relevance():
    ind_test_idf = Indexer(["test_idf_wiki.xml", "title_file.txt", "", "words_file.txt"])
    expected_rel = [
        [math.log(2), math.log(4/3), 0, 0],
        [0, 0, math.log(2), math.log(2)],
        [0, math.log(4/3), math.log(2)/2, 0],
        [math.log(2)/2, math.log(4/3)/2, 0, math.log(2)]
    ]
    assert ind_test_idf.relevance == expected_rel

def test_querier():
    args = ["test_idf_wiki.xml", "title_file.txt", "", "words_file.txt"]
    ind_q = Indexer(args)
    querier = Query(args[1:])
    blue_results = querier.retrieve_results(querier.processed_search_terms("blue"))
    assert len(blue_results) == 4
    cat_results = querier.retrieve_results(querier.processed_search_terms("cat"))
    assert len(cat_results) == 0

    args_11 = ["test_wiki_11.xml", "title_file.txt", "", "words_file.txt"]
    ind_11 = Indexer(args_11)
    q11 = Query(args_11[1:])
    # "built" is not in the test wiki, but should return results from stemming
    builds_results = q11.retrieve_results(querier.processed_search_terms("bUiLds"))
    assert len(builds_results) == 10  #even though there are > 10 pages



