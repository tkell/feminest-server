# names from http://www.cs.cmu.edu/Groups/AI/areas/nlp/corpora/names/male.txt

def male_names():
    names = []
    f = open('male.txt')
    for line in f:
        names.append(line.strip())
    return names

def female_names():
    names = []
    f = open('female.txt')
    for line in f:
        names.append(line.strip())
    return names
