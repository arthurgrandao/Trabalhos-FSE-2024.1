from RPi import GPIO
from time import sleep
from datetime import datetime
from entidades.andar import Andar
import json
import os


class CancelaGPIO:
    def __init__(self, filename: str) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '../json', f'{filename}.json')

        with open(json_path, "r") as f:
            file = json.load(f)

        json_outputs = file["outputs"]
        json_inputs = file["inputs"]

        self.servidor_central = file["host_servidor_central"]
        self.porta_central = file["port_servidor_central"]
        self.host = file["host"]
        self.port = file["port"]
        self.nome = file["nome"]

        for item in json_outputs:
            if item["tag"] == "MOTOR_CANCELA_ENTRADA":
                self.motor_cancela_entrada = item["gpio"]
            elif item["tag"] == "MOTOR_CANCELA_SAIDA":
                self.motor_cancela_saida = item["gpio"]
        for item in json_inputs:
            if item["tag"] == "SENSOR_ABERTURA_CANCELA_ENTRADA":
                self.sensor_abertura_entrada = item["gpio"]
            elif item["tag"] == "SENSOR_FECHAMENTO_CANCELA_ENTRADA":
                self.sensor_fechamento_entrada = item["gpio"]
            elif item["tag"] == "SENSOR_ABERTURA_CANCELA_SAIDA":
                self.sensor_abertura_saida = item["gpio"]
            elif item["tag"] == "SENSOR_FECHAMENTO_CANCELA_SAIDA":
                self.sensor_fechamento_saida = item["gpio"]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Cancela Entrada
        GPIO.setup(self.sensor_abertura_entrada, GPIO.IN)
        GPIO.setup(self.sensor_fechamento_entrada, GPIO.IN)
        GPIO.setup(self.motor_cancela_entrada, GPIO.OUT)
        GPIO.output(self.motor_cancela_entrada, GPIO.LOW)

        # Cancela Saida
        GPIO.setup(self.sensor_abertura_saida, GPIO.IN)
        GPIO.setup(self.sensor_fechamento_saida, GPIO.IN)
        GPIO.setup(self.motor_cancela_saida, GPIO.OUT)
        GPIO.output(self.motor_cancela_saida, GPIO.LOW)

    def abrir_cancela_entrada(self):
        GPIO.output(self.motor_cancela_entrada, GPIO.HIGH)

    def fechar_cancela_entrada(self):
        GPIO.output(self.motor_cancela_entrada, GPIO.LOW)

    def abrir_cancela_saida(self):
        GPIO.output(self.motor_cancela_saida, GPIO.HIGH)

    def fechar_cancela_saida(self):
        GPIO.output(self.motor_cancela_saida, GPIO.LOW)

    def verificar_sensor_abertura_entrada(self) -> bool:
        return GPIO.input(self.sensor_abertura_entrada) == 1

    def verificar_sensor_fechamento_entrada(self) -> bool:
        return GPIO.input(self.sensor_fechamento_entrada) == 1

    def verificar_sensor_abertura_saida(self) -> bool:
        return GPIO.input(self.sensor_abertura_saida) == 1

    def verificar_sensor_fechamento_saida(self) -> bool:
        return GPIO.input(self.sensor_fechamento_saida) == 1


class Cancela:
    def __init__(self, filename: str, andar: Andar) -> None:
        self.gpio = CancelaGPIO(filename)
        self.cliente = andar.cliente_andar
        self.andar = andar

    def enviar_info_entrada(self) -> None:
        current_datetime = datetime.now()
        data = {"message": "entrou_cancela", "piso": "terreo", "data": current_datetime.strftime("%m/%d/%Y, %H:%M:%S")}
        self.cliente.send_to(data, self.cliente.ip, self.gpio.porta_central)

    def enviar_info_saida(self) -> None:
        current_datetime = datetime.now()
        data = {"message": "saiu_cancela", "piso": "terreo", "data": current_datetime.strftime("%m/%d/%Y, %H:%M:%S")}
        self.cliente.send_to(data, self.cliente.ip, self.gpio.porta_central)

    def monitorar_entrada(self) -> None:
        while self.andar.rodando:
            if self.gpio.verificar_sensor_abertura_entrada():
                if GPIO.input(self.gpio.motor_cancela_entrada) == GPIO.LOW:
                    self.enviar_info_entrada()
                self.gpio.abrir_cancela_entrada()
            if self.gpio.verificar_sensor_fechamento_entrada():
                self.gpio.fechar_cancela_entrada()
            sleep(0.2)

    def monitorar_saida(self) -> None:
        while self.andar.rodando:
            if self.gpio.verificar_sensor_abertura_saida():
                sleep(1)
                if GPIO.input(self.gpio.motor_cancela_saida) == GPIO.LOW:
                    self.enviar_info_saida()
                self.gpio.abrir_cancela_saida()
            if self.gpio.verificar_sensor_fechamento_saida():
                self.gpio.fechar_cancela_saida()
            sleep(0.2)
