import RPi.GPIO as GPIO
import struct

ANDARES = ['ST', 'S1', 'S2', 'S3']
PADRAO = {'ST': 1800, 'S1': 5000, 'S2': 13000, 'S3': 2100}

class Sensor:
    def __init__(self, id, uart, lock) -> None:
        self.id = id
        self.uart = uart
        self.lock = lock
        self.ST_PIN = 18 if id == 1 else 17
        self.S1_PIN = 23 if id == 1 else 27
        self.S2_PIN = 24 if id == 1 else 22
        self.S3_PIN = 25 if id == 1 else 6

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.ST_PIN, GPIO.IN)
        GPIO.setup(self.S1_PIN, GPIO.IN)
        GPIO.setup(self.S2_PIN, GPIO.IN)
        GPIO.setup(self.S3_PIN, GPIO.IN)

        self.active_sensor = None

        self.pos_subida = {'ST': 0, 'S1': 0, 'S2': 0, 'S3': 0}
        self.pos_descida = {'ST': 0, 'S1': 0, 'S2': 0, 'S3': 0}
        self.pos_andares = {'ST': 0, 'S1': 0, 'S2': 0, 'S3': 0}
        
        self.calibrando = True

    def posicao(self):
        if self.id == 1:
            cmd = bytes([0x01, 0x23, 0xC1, 0x00]) + bytes([9, 4, 3, 9])
        else:
            cmd = bytes([0x01, 0x23, 0xC1, 0x01]) + bytes([9, 4, 3, 9])

        self.uart.escreverEncoder(cmd, len(cmd))
        response = self.uart.lerEncoder()
        
        if isinstance(response, str):
            response = response.encode('utf-8')
        
        if len(response) != 4:
            print(f'Erro: Esperava 4 bytes, mas recebeu {len(response)} bytes.')
            return None
        
        return struct.unpack('i', response)[0]

    def setCalibrando(self, valor: bool) -> None:
        self.calibrando = valor

    def start(self):
        GPIO.add_event_detect(self.ST_PIN, GPIO.BOTH, callback=self.sensor_callback_subida, bouncetime=200)
        GPIO.add_event_detect(self.S1_PIN, GPIO.BOTH, callback=self.sensor_callback_subida, bouncetime=200)
        GPIO.add_event_detect(self.S2_PIN, GPIO.BOTH, callback=self.sensor_callback_subida, bouncetime=200)
        GPIO.add_event_detect(self.S3_PIN, GPIO.BOTH, callback=self.sensor_callback_subida, bouncetime=200)

    def sensor_callback_subida(self, channel):
        if self.calibrando:
            with self.lock:
                if channel == self.ST_PIN and self.active_sensor != "ST":
                    self.active_sensor = "ST"
                    self.pos_subida[self.active_sensor] = self.posicao()
                elif channel == self.ST_PIN and self.active_sensor == "ST":
                    self.pos_descida[self.active_sensor] = self.posicao()
                elif channel == self.S1_PIN and self.active_sensor != "S1":
                    self.active_sensor = "S1"
                    self.pos_subida[self.active_sensor] = self.posicao()
                elif channel == self.S1_PIN and self.active_sensor == "S1":
                    self.pos_descida[self.active_sensor] = self.posicao()
                elif channel == self.S2_PIN and self.active_sensor != "S2":
                    self.active_sensor = "S2"
                    self.pos_subida[self.active_sensor] = self.posicao()
                elif channel == self.S2_PIN and self.active_sensor == "S2":
                    self.pos_descida[self.active_sensor] = self.posicao()
                elif channel == self.S3_PIN and self.active_sensor != "S3":
                    self.active_sensor = "S3"
                    self.pos_subida[self.active_sensor] = self.posicao()
                elif channel == self.S3_PIN and self.active_sensor == "S3":
                    self.pos_descida[self.active_sensor] = self.posicao()
        else:
            if channel == self.ST_PIN:
                self.active_sensor = "ST"
            elif channel == self.S1_PIN:
                self.active_sensor = "S1"
            elif channel == self.S2_PIN:
                self.active_sensor = "S2"
            elif channel == self.S3_PIN:
                self.active_sensor = "S3"
        
    def calibrar(self):
        for andar, sub, des in zip(ANDARES, self.pos_subida.values(), self.pos_descida.values()):
            if sub == 0 or des == 0:
                self.pos_andares[andar] = (sub + des)
            elif sub == 0 and des == 0:
                self.pos_andares[andar] = PADRAO[andar]
            else:
                self.pos_andares[andar] = (sub + des) // 2    

    def stop(self):
        GPIO.remove_event_detect(self.ST_PIN)
        GPIO.remove_event_detect(self.S1_PIN)
        GPIO.remove_event_detect(self.S2_PIN)
        GPIO.remove_event_detect(self.S3_PIN)

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
