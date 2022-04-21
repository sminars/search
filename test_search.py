import pytest
from index import *

def test_word_processing():
    ind = Indexer(["small_test_wiki.xml", "", "", ""])
    print(ind.corpus)
    assert len(ind.corpus) == 27
    
    