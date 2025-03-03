# Sistema de Gestão de Estacionamento

Este projeto implementa um sistema de gestão de estacionamento distribuído, utilizando servidores para monitorar e gerenciar o fluxo de carros em diferentes andares. O servidor central se comunica com servidores distribuídos para manter atualizadas as informações sobre o número de carros, vagas disponíveis, e a receita gerada.

### 👨‍💻 Contribuidores

<table>
  <tr>
    <td align="center"><a href="https://github.com/G16C"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/G16C?v=4" width="100px;" alt=""/><br /><b>Gabriel Campello</b></a><br />Matrícula: 211039439</td>
    <td align="center"><a href="https://github.com/arthurgrandao"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/arthurgrandao?v=4" width="100px;" alt=""/><br /><b>Arthur Grandão</b></a><br />Matrícula: 211039250</td>
  </tr>
</table>

## Sumário

- [Instalação](#instalação)
- [Uso](#uso)
- [Apresentação](#apresentação)

## Instalação

### Requisitos

- [Python](https://www.python.org/), [pip](https://pypi.org/project/pip/), [git](https://git-scm.com/)
- Bibliotecas Python: `socket`, `threading`, `json`, `time`, `RPi.GPIO`

### Passos de Execução

1. Clone o repositório:
```sh
https://github.com/FGA-FSE/trabalho-1-estacionamentos-embarcadosag.git
```
2. Caso não tenha instalado, instale a biblioteca RPi.GPIO:
```sh
pip install RPi.GPIO==0.7.1
```

## Uso

1. Abra o projeto no terminal e insira:
  
```sh
export PYTHONPATH=/home/<usuario>/<caminho-ate-o-repositorio>/trabalho-1-estacionamentos-embarcadosag/src:$PYTHONPATH
```

Para rodar o projeto inteiro de uma vez:


1. Rode o projeto a partir diretório raiz:

```sh
python3 -m src.main
```

Alternativamente, podemos rodá-lo por módulos:

1. Abra quatro janelas de terminal, tendo o repositório como a raiz.

2. Rode os seguintes comandos, cada um em uma janela:

```sh
python3 -m src.central.main
```

```sh
python3 -m src.terreo.main
```

```sh
python3 -m src.piso1.main
```

```sh
python3 -m src.piso2.main
```
## Apresentação

[Link para a apresentação](https://www.youtube.com/watch?v=9Bse7T69u0E)
