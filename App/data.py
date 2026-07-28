"""
App/data.py

Permet l'import d'une liste de noms propre "DataClass.NAMELIST:list[str]"
"""

DATA=[]
with open("./dumb_wordlist/name_list.txt", "r") as f:
    DATA=f.read().split("\n")

class DataClass:
    NAMELIST=DATA