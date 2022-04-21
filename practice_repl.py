if __name__ == "__main__":
    while True is True:
        response = input("Give me a string to capitalize: ")
        if response == ':quit':
            break
        print(response.upper())

# we would take response and split() it by spaces into a list of words, and 
# instead of printing the response in upper case, we 
# create a querier object and pass the list of words in, and then the querier
# spits out a list of the top 10 page ids, and we set up a helper to convert the 
# page id's to page names and arrange it in a nice string for the repl to print

# two possibilities: either we have 4 arguments and none of them are --pagerank
# or we have 5 arguments and the 1st one is pagerank.  we have if statements to
# check that it's one of these two cases, and then if it is a pagerank case, we
# convey that to our helpers so they know to do the additional page rank calcs
# when giving us our results