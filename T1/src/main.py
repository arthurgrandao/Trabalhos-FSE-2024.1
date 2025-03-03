from terreo.main import main as terreo
from piso1.main import main as piso1
from piso2.main import main as piso2
from central.main import main as central


if __name__ == "__main__":
    try:
        threads = []
        threads.extend(terreo())
        threads.extend(piso1())
        threads.extend(piso2())
        threads.extend(central())

        for thread in threads:
            thread.join()

    except Exception as erro:
        if Exception == KeyboardInterrupt:
            print("Finalizando execução...")
        else:
            print(str(erro))
        exit(0)
