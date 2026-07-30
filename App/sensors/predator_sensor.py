"""
App/sensors/predator_sensor.py

Interface pour le système de capteur des predateurs.

classe surchargée : App/sensors/sensors
"""

from App.sensors.sensors import SensorSystem
from App.vars import *
class PredatorSensorSystem(SensorSystem):
    def __init__(
            self, 

            ):
        super().__init__(PREDATOR.ray_count, PREDATOR.field_of_view, PREDATOR.max_distance)