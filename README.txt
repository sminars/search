Ethan McIntosh and Samantha Minars

# ------------ Background and instructions for use ----------------------

Our search engine is built around two classes - an Indexer (index.py) and a 
Query (query.py).  The Indexer counts and scores words within a corpus of XML
pages and writes that information to local .txt files, which are what the Query
reads in in order to return fast and relevant search results.  To our knowledge,
there are no bugs in our implementation of the search engine.  The first step in
running this program is to run index.py in a terminal using 4 arguments...

index.py <wiki-pages>.xml <title-file>.txt <docs-file>.txt <words-file>.txt

...where <wiki-pages> is the name of a local xml file with a series of tagged
pages, each of which must have a title, a page ID, and text with links denoted 
in standard double-bracket markdown notation, and the three text files are the 
names of text files that will be written locally to be used by the querier.  

Once the indexer is done running, the querier can be run with 1 of 2 commands...

query.py <title-file>.txt <docs-file>.txt <words-file>.txt

or

query.py --pagerank <title-file>.txt <docs-file>.txt <words-file>.txt

...where the names of the .txt files are the same as the ones that were used in
to index the pages.  Including the optional --pagerank flag will yield results 
in which PageRank scores are factored in, not just term relevance scores.

Running query.py will yield an input dialog box on the user's Python console, 
where users can enter search terms and see the titles of the top 10 results for
each query.  To exit the querier, users can type :quit into the dialog box.  

# ---------------- How the search engine works --------------------------

Calculating term relevance and PageRank scores requires a significant number of
intermediate computations using information about words and pages that can only
be known after all words on all pages have been scanned.  Our indexer is 
designed to pre-compute as much as possible while words and pages are being
scanned on a single pass, reducing the amount of post-computation.

First, we perform an initial loop through the pages (the get_pages() method), 
extracting the titles and page IDs of each page so that we can look up whether 
links are in the corpus and so that we know ahead of time how many pages exist.

Then, we loop through all the words in all the pages of the corpus, counting 
frequencies of words on pages and recording the page IDs of every valid link 
while keeping track of the maximum word frequency for each page and the number
of unique document appearances for each word (the process_pages() method).  To 
bundle together multiple types of information about individual words and 
individual pages, we built WordInfo and PageInfo classes and used objects of 
those classes as the values of hashtables keyed on words and pages.  To reduce
the space complexity of our program, we only stored nonzero word counts and 
valid links in these hashtables, instead of using a two-dimensional array or 
another structure in which we'd be storing zeroes whenever a word doesn't appear 
on a page.

Once these hashtables of WordInfos and PageInfos were populated, we were able to
calculate term relevance scores for each word that appeared on each page (the
calc_relevance() method) and then use an iterative approach to generate PageRank
scores based on the weights that each page gives to each other page (the 
calc_ranks() method).  Instead of storing weight values in a data structure, we 
opted to simply store the IDs of valid links in the hashtable of PageInfos and 
then calculate weights on the fly based on each page's number of unique links
(the calc_weights() method).  

The indexer writes the term relevance and PageRank scores to local .txt files
using methods in file_io.py.  These files are then read into hashtables upon
instantiation of a Query object.  Each user search then just involves searching
the page IDs of the pages on which each word of the query appears, storing their
relevance scores (and PageRank scores, if specified) in a list, and then sorting
the list to return the top 10 results.  If words in the query appear on fewer 
than 10 pages, fewer than 10 results will be displayed, and if no pages match 
the query, a message indicating the lack of results will be printed.  

Both the indexer and the querier handle misspelled file names or invalid sets of
command-line arguments using try-except blocks that print out useful messages.  

# ------------------ Testing the search engine -------------------------------
description of how you tested your program, and ALL of your system tests

Examples of system tests include testing various queries and pasting the results.

# --------------- Error catching --------------------------

>> python query.py --pagerank title_file.txt docs_file.txt words_file.tx
File not found -- try again.

>> python query.py --pagerak title_file.txt docs_file.txt words_file.txt
Invalid command line arguments, try again.  Arguments must take the form: 
    --pagerank <title-file>.txt <docs-file>.txt <words-file>.txt
where --pagerank is an optional argument.

>> python query.py --pagerank title_file.txt docs_file.txt
Invalid command line arguments, try again.  Arguments must take the form: 
    --pagerank <title-file>.txt <docs-file>.txt <words-file>.txt
where --pagerank is an optional argument.

>> python query.py title_file.txt docs_file.txt                            
Invalid command line arguments, try again.  Arguments must take the form: 
    --pagerank <title-file>.txt <docs-file>.txt <words-file>.txt
where --pagerank is an optional argument.

>> python query.py title_file.txt docs_file.txt words_file.txt README.txt
Invalid command line arguments, try again.  Arguments must take the form: 
    --pagerank <title-file>.txt <docs-file>.txt <words-file>.txt
where --pagerank is an optional argument.

These tests demonstrate that the querier handles both misspellings of file names
and invalid sets of arguments (including commands with the right number of 
arguments but the wrong types) by printing out informative messages.

# -------------- Handling no results ---------------------

>> python index.py BigWiki.xml title_file.txt docs_file.txt words_file.txt
File successfully indexed!

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt
Search for pages here: the  
No results for that search.
Search for pages here:
No results for that search.
Search for pages here:  
No results for that search.
Search for pages here: " "
No results for that search.
Search for pages here: hgoihnj
No results for that search.

These tests confirm that the search engine correctly handles stop words, empty 
strings, spaces & quote marks, and words not in the corpus by not indexing those
things and by printing out an informative message when they are searched for.

# -------------- testing pagerank's influence -------------

>> python index.py test_pr_wiki.xml title_file.txt docs_file.txt words_file.txt
File successfully indexed!

>> python query.py title_file.txt docs_file.txt words_file.txt             
Search for pages here: tall
1 New York City
2 Skyscrapers

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt  
Search for pages here: tall
1 Skyscrapers
2 New York City

We set up test_pr_wiki such that the word "tall" appears more frequently on the 
New York City page, but that Skyscrapers is linked more by other pages.  This
test confirms that using pagerank or not changes which of those two pages is 
listed first in the search results for the word "tall".

# --------------- BigWiki.xml examples --------------------

>> python index.py BigWiki.xml title_file.txt docs_file.txt words_file.txt
File successfully indexed!

# --- "geopolitical conflict" with and without pagerank ---

>> python query.py title_file.txt docs_file.txt words_file.txt
Search for pages here: geopolitical conflict
1 List of conflicts in the Near East
2 FSF
3 Psychoanalysis
4 Front line
5 Protocol on Environmental Protection to the Antarctic Treaty
6 Guerrilla warfare
7 Irredentism
8 Family law
9 Organization for Security and Co-operation in Europe
10 Fuel-air explosive

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt
Search for pages here: geopolitical conflict
1 Middle Ages
2 Holy Roman Empire
3 Middle East
4 Organization for Security and Co-operation in Europe
5 Pakistan
6 North Africa
7 Indonesia
8 NATO
9 Ottoman Empire
10 Far East

# ------ "dark ages" with and without pagerank -------

>> python query.py title_file.txt docs_file.txt words_file.txt
Search for pages here: dark ages
1 Heart of Darkness
2 Middle Ages
3 Iron Age
4 Hellenic Greece
5 Demographics of Macau
6 Laura Bertram
7 Free-running sleep
8 Neogene
9 Historical revisionism
10 Four-poster

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt
Search for pages here: dark ages
1 Middle Ages
2 Iron Age
3 Mesopotamia
4 Neolithic
5 Holy Roman Empire
6 India
7 Norway
8 Heart of Darkness
9 Germanic peoples
10 Indo-European languages

In both of these examples from BigWiki, the non-pagerank results tend to be more 
obscure pages (FSF, Front line, Irredentism, Laura Bertram, Four-poster) while 
results with pagerank factored in tend to be pages on more well-known topics, 
which we can reasonably assume will have more links to them and thus higher 
PageRank scores.  This helped us confirm that our overall implementation of 
PageRank is working as intended in both the indexing and querying components.

# ----------- Selected MedWiki.xml TA examples --------

>> python index.py MedWiki.xml title_file.txt docs_file.txt words_file.txt
File successfully indexed!

# ---- "baseball" with and without pagerank -----

>> python query.py title_file.txt docs_file.txt words_file.txt
Search for pages here: baseball
1 Oakland Athletics
2 Minor league baseball
3 Kenesaw Mountain Landis
4 Miami Marlins
5 Fantasy sport
6 Out
7 October 30
8 January 7
9 Hub
10 February 2

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt
Search for pages here: baseball
1 Ohio
2 February 2
3 Oakland Athletics
4 Kenesaw Mountain Landis
5 Netherlands
6 Miami Marlins
7 Minor league baseball
8 Kansas
9 Pennsylvania
10 Fantasy sport

# --- "United States" with and without pagerank ---

>> python query.py title_file.txt docs_file.txt words_file.txt
Search for pages here: United States
1 Federated States of Micronesia
2 Imperial units
3 Joule
4 Knowledge Aided Retrieval in Activity Context
5 Imperialism in Asia
6 Elbridge Gerry
7 Martin Van Buren
8 Pennsylvania
9 Finite-state machine
10 Metastability

>> python query.py --pagerank title_file.txt docs_file.txt words_file.txt
Search for pages here: United States
1 Netherlands
2 Ohio
3 Illinois
4 Michigan
5 Pakistan
6 International Criminal Court
7 Franklin D. Roosevelt
8 Pennsylvania
9 Norway
10 Louisiana

These examples of searches in MedWiki.xml closely match the TA examples, further
confirming that our algorithms prioritize pages correctly for both term
relevance only and with PageRank factored in.