"""
App/sensors/preys_sensor.py

Interface pour le système de capteur des proies

classe surchargée : App/sensors/sensors
"""
from App.sensors.sensors import SensorSystem
from App.vars import *
class PreySensorSystem(SensorSystem):
    def __init__(
            self 
            ):
        super().__init__(PREY.ray_count, PREY.field_of_view, PREY.max_distance)