import requests

URL = "http://upe.42069.fun/rAulD"
DICT = "currentdict.txt" #The main dictionary file which will be altered
TEMPDICT = "tempdict.txt" #A temporary dictionary file used for updating DICT
CUSTOMDICT = "customdict.txt" #A custom dictionary created from the lyrics found in this hangman game

FREQ_ALPHA = "eariotnslcudpmhgbfywkvxzjq" #frequency based ordering of the alphabet
BAD_CHARS = [',', '?', '!', ';', '"', '(', ')', '{', '}'] #chars that will be removed from dictionary and state
EMPHASIS = 1 #The extra frequency emphasis added for words not guessed

#removes all words from dictionary which don't fit in the state
def updateDictFromState(state):
    for c in BAD_CHARS:
        state = state.replace(c, '')
    state = state.replace('-', ' ')
    state = state.split(' ')    
    
    with open(DICT, 'r') as fIn:
        with open(TEMPDICT, 'w+') as fOut:
            for w in fIn.readlines():
                write = False

                for stateWord in state:
                    if '_' in stateWord:
                        
                        temp = w.replace("\n", "")
                        temp = list(w.split(" ")[0])
                        
                        for i in range(min(len(temp),len(stateWord))):
                            if temp[i].isalpha() and stateWord[i] == '_':
                                temp[i] = '_'
                    
                        temp = "".join(temp)
                    
                        if temp == stateWord:
                            write = True
                
                if write:
                    fOut.write(w)
    
    with open(TEMPDICT, 'r') as fIn:
        with open(DICT, 'w') as fOut:
            fOut.write(fIn.read())

#removes all words from dictionary which contain the character char (Which is was a failed hangman guess)
def updateDictFromFailure(char):
    with open(DICT, 'r') as fIn:
        with open(TEMPDICT, 'w') as fOut:
            for w in fIn.readlines():
                if char not in w:
                    fOut.write(w)
                    
    with open(TEMPDICT, 'r') as fIn:
        with open(DICT, 'w') as fOut:
            fOut.write(fIn.read())

#Returns a dict (the object) of how often each character shows up in the actual dictionary
def getCharFreq():
    freq = dict.fromkeys(FREQ_ALPHA, 0)  
    
    with open(DICT, 'r') as f:
        for w in f.readlines():
            w = w.replace("\n", "")
            w = w.split(" ")
            for c in FREQ_ALPHA:
                if c in w[0]:
                    freq[c] += int(w[1])

    return freq
    
#takes the answer from a hangman game (lyrics field) and adds each word to the custom dictionary
def addToCustomDict(words):
    for c in BAD_CHARS:
        words = words.replace(c, "")
    words = words.replace("-", " ")
    words = words.split(" ")
    
    with open(CUSTOMDICT, 'r') as fIn:
        with open(TEMPDICT, 'w') as fOut:
            for w in fIn.readlines():
                w = w.replace("\n","")
                w = w.split(" ")
                while w[0] in words:
                    w[1] = str(1 + int(w[1]))
                    words.remove(w[0])
                
                fOut.write(w[0] + " " + w[1] + "\n")
            
            for newWord in words:
                containsLetters = False
                for c in newWord:
                    if c.isalpha():
                        containsLetters = True
                if containsLetters:
                    fOut.write(newWord + " 1\n")
                
    with open(TEMPDICT, 'r') as fIn:
        with open(CUSTOMDICT, 'w') as fOut:
            fOut.write(fIn.read())
            
            
#Same as last function, except words which weren't guessed get extra emphasis
def addToCustomDictWithEmphasis(words, state): 
    for c in BAD_CHARS:
        words = words.replace(c, "")
        state = state.replace(c, "")
    words = words.replace("-", " ")
    words = words.split(" ")
    state = state.replace("-", " ")
    state = state.split(" ")
    
    with open(CUSTOMDICT, 'r') as fIn:
        with open(TEMPDICT, 'w') as fOut:
            for w in fIn.readlines():
                w = w.replace("\n","")
                w = w.split(" ")
                while w[0] in words:
                    w[1] = str(1 + int(w[1]))
                    words.remove(w[0])
                    
                    #add extra frequency emphasis for words that weren't completely solved
                    if w[0] not in state:
                        w[1] = str(EMPHASIS + int(w[1]))
                
                fOut.write(w[0] + " " + w[1] + "\n")
            
            for newWord in words:
                containsLetters = False
                for c in newWord:
                    if c.isalpha():
                        containsLetters = True
                if containsLetters:
                    if newWord not in state:
                        fOut.write(newWord + " " + str(EMPHASIS + 1) + "\n")
                    else:
                        fOut.write(newWord + " " + str(1) + "\n")
                
    with open(TEMPDICT, 'r') as fIn:
        with open(CUSTOMDICT, 'w') as fOut:
            fOut.write(fIn.read())


def main():
    while True:    
        
        #copy main dictionary file into a file called DICT or currentdict.txt which will be changed throughout this round
        with open(CUSTOMDICT, 'r') as fIn:
            with open(DICT, 'w+') as fOut:
                fOut.write(fIn.read())
        
        
        #Play one game
        r = requests.get(url = URL)
        
        data = r.json()
    
        #MAINTAIN SET OF FAILED CHARS
        all_guesses = set()
        
        while data['status'] == "ALIVE":
            updateDictFromState(data['state'])
            
            freq = getCharFreq()
            for c in FREQ_ALPHA:
                if c not in all_guesses:
                    guess = c
            for c in freq:
                if freq[guess] < freq[c] and c not in all_guesses:
                    guess = c
            
            post = {'guess':guess}
            all_guesses.add(guess)
            
            previous_guesses = data['remaining_guesses']
            
            r = requests.post(url = URL, data = post)
            data = r.json()
            
            if (data['remaining_guesses'] < previous_guesses):
                updateDictFromFailure(guess)
        
        if 'lyrics' in data:
            addToCustomDictWithEmphasis(data['lyrics'], data['state'])
                
        print(data['status'])
        print("Games:",data['games'])
        print("Win Rate:", data['win_rate'])
        print(data['state'])
        print(data['lyrics'])
        print()
    

if __name__ == "__main__":
    main()