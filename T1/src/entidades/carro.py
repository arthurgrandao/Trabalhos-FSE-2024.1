import itertools


class Carro:
    id_iter = itertools.count()

    def __init__(self) -> None:
        self.id = next(self.id_iter)
        self.tempo_saida = None
        self.piso = None
        self.vaga = None
        self.preco_total = None
        self.tempo_entrada = None

    def calcula_preco_total(self):
        diferenca_tempo = (self.tempo_saida - self.tempo_entrada).total_seconds()/60
        self.preco_total = 0.15 * diferenca_tempo

    def to_string(self):
        f"Carro: {self.id} - Vaga: {self.vaga} - Entrada: {self.tempo_entrada} - Saida: {self.tempo_saida} - R$ {self.preco_total}"
