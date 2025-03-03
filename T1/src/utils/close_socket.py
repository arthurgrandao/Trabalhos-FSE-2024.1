import socket

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.bind(("localhost", 10691))
sock1.close()

sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2.bind(("localhost", 10700))
sock2.close()

sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock3.bind(("localhost", 10710))
sock3.close()

sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock4.bind(("localhost", 10701))
sock4.close()