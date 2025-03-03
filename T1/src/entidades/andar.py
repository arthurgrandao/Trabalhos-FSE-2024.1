import RPi.GPIO as GPIO
import time
import json
import os

from src.conexao.conexao import Cliente, Servidor


class AndarGPIO:
    def __init__(self, filename: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '../json', f'{filename}.json')

        with open(json_path, "r") as f:
            file = json.load(f)

        json_outputs = file["outputs"]
        json_inputs = file["inputs"]

        self.host = "localhost"
        self.port = file["port"]
        self.nome = file["nome"]

        for item in json_outputs:
            if item["tag"] == "ENDERECO_01":
                self.endereco_1 = item["gpio"]
            elif item["tag"] == "ENDERECO_02":
                self.endereco_2 = item["gpio"]
            elif item["tag"] == "ENDERECO_03":
                self.endereco_3 = item["gpio"]
            elif item["tag"] == "SINAL_DE_LOTADO_FECHADO":
                self.sinal_led_lotado = item["gpio"]

        for item in json_inputs:
            if item["tag"] == "SENSOR_DE_VAGA":
                self.sensor_vaga = item["gpio"]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.sinal_led_lotado, GPIO.OUT)
        GPIO.setup(self.endereco_1, GPIO.OUT)
        GPIO.setup(self.endereco_2, GPIO.OUT)
        GPIO.setup(self.endereco_3, GPIO.OUT)
        GPIO.setup(self.sensor_vaga, GPIO.IN)

        # Define os valores das vagas
        self.output_values = [[GPIO.LOW, GPIO.LOW, GPIO.LOW],    # 1
                             [GPIO.LOW, GPIO.LOW, GPIO.HIGH],     # 2
                             [GPIO.LOW, GPIO.HIGH, GPIO.LOW],     # 3
                             [GPIO.LOW, GPIO.HIGH, GPIO.HIGH],    # 4
                             [GPIO.HIGH, GPIO.LOW, GPIO.LOW],     # 5
                             [GPIO.HIGH, GPIO.LOW, GPIO.HIGH],    # 6
                             [GPIO.HIGH, GPIO.HIGH, GPIO.LOW],    # 7
                             [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]]   # 8

    def liga_sinal_led_lotado(self):
        GPIO.output(self.sinal_led_lotado, GPIO.HIGH)

    def apaga_sinal_led_lotado(self):
        GPIO.output(self.sinal_led_lotado, GPIO.LOW)


class Andar:
    def __init__(self, filename: str) -> None:
        self.num_carros = 0
        self.vagas = [0,0,0,0,0,0,0,0]

        self.gpio = AndarGPIO(filename)

        self.host = "localhost"
        self.port = self.gpio.port
        self.nome = self.gpio.nome

        self.endereco_central = "localhost"
        self.porta_central = 10701

        self.cliente_andar = Cliente(self.endereco_central, self.porta_central)
        self.servidor_andar = Servidor(self.gpio.host, self.gpio.port)

        self.fechamento_manual = False
        self.rodando = True

    def receber_info(self):
        while self.rodando:
            try:
                conexao, endereco = self.servidor_andar.accept()

                data = conexao.recv(2048).decode()
                data_json = json.loads(data)

                if data_json["message"] == "finalizar":
                    self.rodando = False
                    self.servidor_andar.close()
                    print(f"{self.nome} finalizando.")
                    continue

                if data_json["message"] == "ativar_led_lotado" and data_json["manual"] == True:
                    self.gpio.liga_sinal_led_lotado()
                    self.fechamento_manual = True

                if data_json["message"] == "desativar_led_lotado" and data_json["manual"] == True:
                    self.gpio.apaga_sinal_led_lotado()
                    self.fechamento_manual = False

                if data_json["message"] == "ativar_led_lotado" and data_json["manual"] == False and not self.fechamento_manual:
                    self.gpio.liga_sinal_led_lotado()

                if data_json["message"] == "desativar_led_lotado" and data_json["manual"] == False and not self.fechamento_manual:
                    self.gpio.apaga_sinal_led_lotado()

                conexao.close()

                time.sleep(0.1)
            except Exception as erro:
                print(f"Erro na conexão receber info: {erro}")
                time.sleep(0.5)

    def enviar_info(self):
        print(f"{self.gpio.nome} - {self.gpio.host}:{self.gpio.port}")
        while self.rodando:
            try:
                for i in range(8):
                    GPIO.output(self.gpio.endereco_3, self.gpio.output_values[i][0])
                    GPIO.output(self.gpio.endereco_2, self.gpio.output_values[i][1])
                    GPIO.output(self.gpio.endereco_1, self.gpio.output_values[i][2])
                    time.sleep(0.2)
                    sensor_vaga = GPIO.input(self.gpio.sensor_vaga)

                    if sensor_vaga != self.vagas[i]:
                        self.vagas[i] = sensor_vaga

                        if sensor_vaga:
                            data = {"message": "estacionou_carro", "piso": f"{self.nome}", "endereco": i}
                        else:
                            data = {"message": "saiu_carro", "piso": f"{self.nome}", "endereco": i}

                        self.cliente_andar.send_to(data, self.endereco_central, self.porta_central)

                time.sleep(0.1)

            except Exception as erro:
                print(f"Erro na conexão enviar info: {erro}")
                time.sleep(0.5)
