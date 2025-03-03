from src.entidades.andar import Andar
from src.entidades.sensor_passagem import SensorPassagem
import threading


def main() -> list[threading.Thread]:
    andar = Andar("piso2")
    sensor_passagem = SensorPassagem("piso2", andar)

    receber = threading.Thread(target=andar.receber_info, daemon=True)
    enviar = threading.Thread(target=andar.enviar_info, daemon=True)
    monitorar_passagem = threading.Thread(target=sensor_passagem.monitorar_passagem, daemon=True)

    receber.start()
    enviar.start()
    monitorar_passagem.start()

    return [receber, enviar, monitorar_passagem]


if __name__ == "_main_":
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
