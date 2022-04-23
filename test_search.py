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
    
    