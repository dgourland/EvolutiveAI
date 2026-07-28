"""
App/death_record.py

Objet stockant des métriques sur une créatures morte
"""

from App.entities.creature import Creature

class DeathRecord:
    def __init__(self, creature:Creature, time):
        
        self.ev={
            "id":id(creature),
            "age":creature.age,
            "food_eaten":creature.score,
            "time":time,
            "fitness": creature.fitness,
            "dna":creature.dna.dumpDna(),
            "distance_traveled": creature.distance_travel,
            "childs": creature.childs,
            "type": creature.type
        }

    def getEvent(self):
        return self.ev