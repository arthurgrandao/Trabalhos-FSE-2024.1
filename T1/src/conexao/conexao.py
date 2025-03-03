import json
import socket

IP_SOCKET_CENTRAL = "localhost"
PORTA_SOCKET_CENTRAL = 10701


class Servidor:
    def __init__(self, ip: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)

    def accept(self):
        return self.sock.accept()

    def bind(self):
        self.sock.bind((self.ip, self.port))

    def listen(self, num=1):
        self.sock.listen(num)

    def send(self, data):
        self.sock.send(json.dumps(data).encode())

    def receive(self):
        return self.sock.recv(2048).decode()

    def receive_dict(self):
        return self.sock.recv(2048)

    def close(self):
        self.sock.close()


class Cliente:
    def __init__(self, ip: str, port: int):
        self.sock = None
        self.ip = ip
        self.port = port

    def send_to(self, data, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(json.dumps(data).encode())
            sock.close()

        except Exception as e:
            print(f"Erro ao enviar dados: {e}")
