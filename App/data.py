DATA=[]
with open("./dumb_wordlist/name_list.txt", "r") as f:
    DATA=f.read().split("\n")

class DataClass:
    NAMELIST=DATA