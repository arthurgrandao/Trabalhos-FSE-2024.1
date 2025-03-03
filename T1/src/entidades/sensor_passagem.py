import json
from time import sleep
from entidades.andar import Andar
import os

import RPi.GPIO as GPIO


class SensorPassagemGPIO:
    def __init__(self, filename: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '../json', f'{filename}.json')

        with open(json_path, "r") as f:
            file = json.load(f)

        json_inputs = file["inputs"]

        for item in json_inputs:
            if item["tag"] == "SENSOR_DE_PASSAGEM_1":
                self.sensor_passagem1 = item["gpio"]
            elif item["tag"] == "SENSOR_DE_PASSAGEM_2":
                self.sensor_passagem2 = item["gpio"]

        GPIO.setup(self.sensor_passagem1, GPIO.IN)
        GPIO.setup(self.sensor_passagem2, GPIO.IN)


class SensorPassagem:
    def __init__(self, filename: str, andar: Andar):
        self.gpio = SensorPassagemGPIO(filename)
        self.cliente = andar.cliente_andar
        self.piso = andar.nome
        self.porta = andar.porta_central
        self.andar = andar
        self.sensores = []

        GPIO.add_event_detect(self.gpio.sensor_passagem1, GPIO.RISING, callback=self.sensor_1_callback, bouncetime=200)
        GPIO.add_event_detect(self.gpio.sensor_passagem2, GPIO.RISING, callback=self.sensor_2_callback, bouncetime=200)

    def sensor_1_callback(self, channel) -> None:
        if not 1 in self.sensores:
            self.sensores.append(1)

    def sensor_2_callback(self, channel) -> None:
        if not 2 in self.sensores:
            self.sensores.append(2)

    def monitorar_passagem(self) -> None:
        while True:
            if not self.andar.rodando:
                GPIO.remove_event_detect(self.gpio.sensor_passagem1)
                GPIO.remove_event_detect(self.gpio.sensor_passagem2)
                break

            if len(self.sensores) == 2:
                if self.sensores[0] == 1 and self.sensores[1] == 2:
                    self.cliente.send_to({"message": "subindo", "piso": self.piso}, self.cliente.ip, self.porta)
                    sleep(0.5)
                    self.sensores = []
                elif self.sensores[0] == 2 and self.sensores[1] == 1:
                    self.cliente.send_to({"message": "descendo", "piso": self.piso}, self.cliente.ip, self.porta)
                    sleep(0.5)
                    self.sensores = []
            sleep(0.1)
