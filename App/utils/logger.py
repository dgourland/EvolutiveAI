"""
logger.py

Gestion des événements de simulation.

Permet de garder une trace :
- morts
- naissances
- générations
- statistiques

"""

import json
from datetime import datetime
import os
from App.death_record import DeathRecord
import numpy as np

def json_serializer(obj):

    if isinstance(obj, np.float32):
        return float(obj)

    if isinstance(obj, np.float64):
        return float(obj)

    if isinstance(obj, np.int32):
        return int(obj)

    if isinstance(obj, np.int64):
        return int(obj)

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    raise TypeError(
        f"{type(obj)} is not JSON serializable"
    )

class SimulationLogger:


    def __init__(
        self,
        filename="simulation_log.json"
        
    ):
        for file in os.listdir("./logs"):
            os.remove("./logs/"+file)
        self.filename = filename

        self.events = [{"cause":"Starting Simulation", "timestamp":datetime.now().isoformat(), "total_score":0}]



    # -------------------------------------------------
    # Enregistrement d'une mort
    # -------------------------------------------------

    def log_death(
        self,
        creature:DeathRecord,
        time,
        generation,
        cause="unknown"
    ):

        event = creature.getEvent()
        event["time"]=time
        event["generation"]=generation
        event["cause"]=cause
        event["real_date"]=datetime.now().isoformat()
        
        

        self.events.append(
            event
        )



    # -------------------------------------------------
    # Sauvegarde fichier
    # -------------------------------------------------

    def save(self, generation):
        with open(
            "./logs/"+str(generation)+" - "+self.filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.events,
                file,
                indent=4,
                default=json_serializer
            )
        self.events=[]


    # -------------------------------------------------
    # Nettoyage
    # -------------------------------------------------

    def clear(self):

        self.events.clear()