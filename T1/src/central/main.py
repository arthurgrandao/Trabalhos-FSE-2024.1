from datetime import datetime
from src.conexao.conexao import Servidor, Cliente
from src.entidades.carro import Carro
import threading
import json
import time
import os


class Central:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'port': 10701,
            'distributed_servers': {
                'terreo': {'host': 'localhost', 'port': 10691},
                'piso1': {'host': 'localhost', 'port': 10700},
                'piso2': {'host': 'localhost', 'port': 10710}
            }
        }
        self.host = self.config['host']
        self.port = self.config['port']
        self.servers = self.config['distributed_servers']
        self.total_carros = 0
        self.total_renda = 0.0
        self.dados_estacionamento = {
            "terreo": {"carros": 0, "spaces": [None] * 8},
            "piso1": {"carros": 0, "spaces": [None] * 8},
            "piso2": {"carros": 0, "spaces": [None] * 8},
        }
        self.lotado = {
            "terreo": False,
            "piso1": False,
            "piso2": False
        }
        self.lock = threading.Lock()
        self.fila_entrada_carros = []
        self.fila_saida_carros = []

        self.servidor_central = Servidor(self.host, self.port)
        self.cliente_central = Cliente(self.host, self.port)
        self.rodando = True

    def listen_updates(self):
        while self.rodando:
            conn, addr = self.servidor_central.accept()
            data = conn.recv(2048).decode()
            if data:
                self.handle_update(json.loads(data))
            conn.close()

    def handle_update(self, data):
        if "piso" in data:
            if data["message"] == "entrou_cancela":
                self.handle_entrada(data)
            elif data["message"] == "saiu_cancela":
                self.handle_saida(data)
            elif data["message"] == "subindo":
                self.handle_passagem_subida(data)
            elif data["message"] == "descendo":
                self.handle_passagem_descida(data)
            elif data["message"] == "estacionou_carro":
                self.handle_estacionamento_vaga(data)
            elif data["message"] == "saiu_carro":
                self.handle_saida_vaga(data)
            self.check_parking_lot_status()

    def handle_passagem_subida(self, data):
        with self.lock:
            if data["piso"] == "piso1":
                self.dados_estacionamento["terreo"]["carros"] -= 1
                self.dados_estacionamento["piso1"]["carros"] += 1
            elif data["piso"] == "piso2":
                self.dados_estacionamento["piso1"]["carros"] -= 1
                self.dados_estacionamento["piso2"]["carros"] += 1

    def handle_passagem_descida(self, data):
        with self.lock:
            if data["piso"] == "piso2":
                self.dados_estacionamento["piso2"]["carros"] -= 1
                self.dados_estacionamento["piso1"]["carros"] += 1
            elif data["piso"] == "piso1":
                self.dados_estacionamento["piso1"]["carros"] -= 1
                self.dados_estacionamento["terreo"]["carros"] += 1

    def handle_estacionamento_vaga(self, data):
        if not self.fila_entrada_carros:
            time.sleep(1)
        self.dados_estacionamento[data["piso"]]["spaces"][data["endereco"]] = self.fila_entrada_carros.pop(0)

    def handle_saida_vaga(self, data):
        with self.lock:
            self.fila_saida_carros.append(self.dados_estacionamento[data["piso"]]["spaces"][data["endereco"]])
            self.dados_estacionamento[data["piso"]]["spaces"][data["endereco"]] = None

    def handle_entrada(self, data):
        with self.lock:
            car_info = Carro()
            car_info.tempo_entrada = datetime.strptime(data["data"], '%m/%d/%Y, %H:%M:%S')

            self.dados_estacionamento["terreo"]["carros"] += 1
            self.total_carros += 1
            self.fila_entrada_carros.append(car_info)

    def handle_saida(self, data):
        with self.lock:
            if not self.fila_saida_carros:
                time.sleep(1)

            try:
                self.fila_saida_carros[0].tempo_saida = datetime.strptime(data["data"], '%m/%d/%Y, %H:%M:%S')

                self.dados_estacionamento["terreo"]["carros"] -= 1
                self.total_carros -= 1
                self.fila_saida_carros[0].calcula_preco_total()
                self.total_renda += self.fila_saida_carros[0].preco_total

                self.fila_saida_carros.pop(0)
            except ValueError as e:
                print(f"Erro ao remover carro de fila_saida_carros: {e}")

    def check_parking_lot_status(self):
        lotado = []
        for piso in ["piso1", "piso2"]:
            if self.dados_estacionamento[piso]["carros"] >= 8:
                self.set_lotado(True, piso)
                lotado.append(True)
            else:
                self.set_lotado(False, piso)
                lotado.append(False)

        if lotado[0] == True and lotado[1] == True:
            self.set_lotado(True, "terreo")
        else:
            self.set_lotado(False, "terreo")

    def set_lotado(self, status, piso, manual=False):
        self.lotado[piso] = status
        message = {"message": "ativar_led_lotado" if status else "desativar_led_lotado", "manual": manual}
        try:
            self.cliente_central.send_to(message, self.servers[piso]["host"], self.servers[piso]["port"])
        except Exception as e:
            print(f"Erro ao enviar mensagem lotado/aberto ao servidor: {e}")

    def block_pisos(self, pisos):
        for piso in pisos:
            if piso in self.servers:
                try:
                    self.lotado[piso] = True
                    server_info = self.servers[piso]
                    self.cliente_central.send_to({"message": "ativar_led_lotado", "manual": True}, server_info["host"], server_info["port"])
                except Exception as e:
                    print(f"Erro ao enviar mensagem de bloqueio ao servidor {piso}: {e}")

    def abrir_pisos(self, pisos):
        for piso in pisos:
            if piso in self.servers:
                try:
                    self.lotado[piso] = False
                    server_info = self.servers[piso]
                    self.cliente_central.send_to({"message": "desativar_led_lotado", "manual": True}, server_info["host"], server_info["port"])
                except Exception as e:
                    print(f"Erro ao enviar mensagem de abertura ao servidor {piso}: {e}")

    def display_status(self) -> str:
        status = ""
        with self.lock:
            status += f"Status estacionamento ({datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}):\n"
            status += "------------------------------\n"
            for piso, data in self.dados_estacionamento.items():
                status += f"{piso.capitalize()} {'Fechado' if self.lotado[piso] else 'Aberto'}\n"
                i = 0
                deficiente = 1
                idoso = 2
                regular = 5
                for space in data['spaces']:
                    if space is not None:
                        status += "| X "

                        if i == 0:
                            deficiente -= 1
                        elif i == 1 or i == 2:
                            idoso -= 1
                        else:
                            regular -= 1
                    else:
                        status += "| O "
                    i += 1
                status += f"| ({data['carros']} carros)({deficiente}/{idoso}/{regular})\n"
            status += f"Valor Total: ${self.total_renda:.2f}"
        return status

    def userinterface(self):
        msg = ""
        while True:
            os.system('clear')
            print("------------------------------")
            print(self.display_status())
            print("------------------------------")
            print("Comandos:")
            print("1. Fechar Estacionamento")
            print("2. Abrir Estacionamento")
            print("3. Bloquear Andares")
            print("4. Abrir Andares")
            print("5. Atualizar Status Estacionamento")
            print("Sair (ctrl+C)")
            print("------------------------------")
            print(f"Última mensagem:\n{msg}")
            print("------------------------------")
            command = input("Entre o numero de comando: ").strip()

            if command == "1":
                self.set_lotado(True, "terreo", True)
                msg = "Estacionamento fechado."
            elif command == "2":
                self.set_lotado(False, "terreo", True)
                msg = "Estacionamento aberto."
            elif command == "3":
                pisos = input("Digite os pisos que deseja fechar (separados por vírgula): ").strip().split(',')
                self.block_pisos(pisos)
                msg = f"Pisos: {pisos} bloqueados."
            elif command == "4":
                pisos = input("Digite os pisos que deseja abrir (separados por vírgula): ").strip().split(',')
                self.abrir_pisos(pisos)
                msg = f"Pisos: {pisos} abertos."
            elif command == "5":
                continue
            else:
                msg = "Comando invalido. Tente novamente."


def main() -> list[threading.Thread]:
    central_server = Central()

    ui = threading.Thread(target=central_server.userinterface, daemon=True)
    listen = threading.Thread(target=central_server.listen_updates, daemon=True)

    ui.start()
    listen.start()

    return [ui, listen]


if __name__ == "__main__":
    try:
        threads = main()

        for thread in threads:
            thread.join()

    except Exception as erro:
        if Exception == KeyboardInterrupt:
            print("Finalizando execução...")
        else:
            print(str(erro))
        exit(0)
