Ethan McIntosh and Samantha Minars

### Background and instructions for use

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

### How the search engine works

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

### Testing the search engine
description of how you tested your program, and ALL of your system tests

Examples of system tests include testing various queries and pasting the results.