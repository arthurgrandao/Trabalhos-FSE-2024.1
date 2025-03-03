from src.entidades.andar import Andar
from src.entidades.cancela import Cancela
import threading


def main() -> list[threading.Thread]:
    andar = Andar("terreo")
    cancela = Cancela("terreo", andar)

    receber = threading.Thread(target=andar.receber_info, daemon=True)
    enviar = threading.Thread(target=andar.enviar_info, daemon=True)
    monitorar_e = threading.Thread(target=cancela.monitorar_entrada, daemon=True)
    monitorar_s = threading.Thread(target=cancela.monitorar_saida, daemon=True)

    receber.start()
    enviar.start()
    monitorar_e.start()
    monitorar_s.start()

    return [receber, enviar, monitorar_e, monitorar_s]


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
