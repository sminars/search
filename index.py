# index.py
import sys

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Must have exactly 4 arguments after index.py -- try again.")
        sys.exit()
    
    print(sys.argv[1])
    print(sys.argv[2])
    print(sys.argv[3])
    print(sys.argv[4])

