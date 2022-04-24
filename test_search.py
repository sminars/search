import pytest
from index import *

def test_word_processing():
    """ensure that Indexer adds the words to the corpus that we'd expect"""
    ind = Indexer(["small_test_wiki.xml", "", "", ""])

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
    
    ind = Indexer(["pipelink_tiny_wiki.xml", "", "", ""])

    assert len(ind.corpus) == len(expected_corpus)
    for word in expected_corpus:
        assert word in ind.corpus

    expected_tf = [
        [1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    ]

   

    assert ind.tf_array == expected_tf
    

def test_idf():
    ind_tiny = Indexer(["pipelink_tiny_wiki.xml", "", "", ""])
    expected_idf = [math.log(2)] * 11
    assert ind_tiny.idf_array == expected_idf

    ind_test_idf = Indexer(["test_idf_wiki.xml", "", "", ""])
    expected = [math.log(2), math.log(4/3), math.log(2), math.log(2)]
    assert ind_test_idf.idf_array == expected

def test_relevance():
    ind_test_idf = Indexer(["test_idf_wiki.xml", "", "", ""])
    expected_rel = [
        [math.log(2), math.log(4/3), 0, 0],
        [0, 0, math.log(2), math.log(2)],
        [0, math.log(4/3), math.log(2)/2, 0],
        [math.log(2)/2, math.log(4/3)/2, 0, math.log(2)]
    ]
    assert ind_test_idf.relevance == expected_rel


