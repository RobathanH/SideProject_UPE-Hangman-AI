# UPE_Hangman_AI

Necessary Files:
- hangman.py
- customdict.txt


How to use:

Run hangman.py in a folder which also includes customdict.txt
- must be run on python 3
- must have python module 'requests' installed
- hangman.py will create new txt files

hangman.py works by maintaining a txt file of all words that it has seen before, and how many times it has seen each one. During a game, it will shorten the list to only words that may fit in the given state, and make a guess based on the most frequent letter in that list.
