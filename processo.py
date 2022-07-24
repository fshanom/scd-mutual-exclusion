# Deve se conectar via socket.
# Possui apenas um socket, e deve conhecer o IP e a porta do coordenador para se conectar ao socket

# Cada processo deve ficar em um loop fazendo requisições de acesso a região críica do coordenador

# O que o processo deve fazer?
# Ao obter acesso, o processo abre o arquivo de log em modo append, obtem a hora atual, escreve seu id e a hora atual incluindo milissegundos no final do arquivo, fecha o arquivo e depois aguarda k segundos usando a função sleep(). Deve ser repetido r vezes, após isso o processo termina.
# Diferentes processos devem executar na mesma máquina e escrever no mesmo arquivo de log. o número de processos é n

# Devem ser todos iniciads sequencialmente, sem retardo, por um script ou um outro processo.
# Uma execução com n processos e r repetições deve dar origem a um arquivo de log com n*r linhas
# Deve ser verificado se o arquivo tem esse número de linhas e se as linhas estão corretas respeitando o relógio, e se cada processo escreveu r vezes.
# Verificar os GRANT e RELEASE, apóis um grant sempre tem release. A ordem dos processos das mensagens REQUEST deve ser a mesma que a ordem dos processos da mensagem Release.



from datetime import datetime
import logging
import socket
import time
from asyncio import Queue
import json
import argparse

#Carrega as configurações do server
with open("config.json", "r") as configFile:
    config = json.load(configFile)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#serv.connect(config["IP"],config["port"])

#Log da RC
logging.basicConfig(filename='resultado.txt', filemode='w', level=logging.INFO)

class Processo:
    def __init__(self, processo_id, num_processo):
        self.id = processo_id
        self.connections = []
        self.number_set = []
        self.processo_count = num_processo
        self.number_set_idx = 0
        #self.get_number_set()
        print("Iniciando Processo "+ str(self.id))
    
    #Método que solicita o acesso para escrita na RC
    def request(self):
        #while len(self.number_set) > self.number_set_idx:

        log = open("resultado.txt", "a")
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M:%S.%f")
        log.write(current_time + " | REQUEST | Processo " + str(self.id) + " | Teste \n")
        log.close()
        #logging.info( current_time + " | REQUEST | Processo " + str(self.id) + " | Teste")

        # lamport
        # 1 envia pedido com timestamp para todos os processos incluindo a si mesmo
        # 2 aguarda confirmação de todos os processos
        # 3 se o pedido estiver na cabeça da fila e todas as confirmações chegarem, entra na RC


        connection = self.__connect(True)
        msg = current_time + ' | REQUEST #' + str(self.id)
        connection.sendall(msg.encode())
        print('Processo ' + str(self.id) + ' mandou solicitação de escrita Coordenador')
        self.connections.append(connection)
        self.number_set_idx = self.number_set_idx + 1
        time.sleep(3)    
    
    
    def get_number_set(self):
        num_file = open(config["log_file"], 'r')
        lines = num_file.readlines()
        for i in range(0, len(lines)):
            if i % self.processo_count == self.id:
                self.number_set.append(int(lines[i]))
        num_file.close()

    #Método que conecta no socket do coordenador
    def __connect(self, retry):
        try:
            to_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            to_socket.connect((config["IP"],config["port"]))
            print("Processo " + str(self.id) + " Conectado")
        except socket.error:
            if retry:
                print("Conexão falhou no processo " + str(self.id))
                time.sleep(2)
                return self.__connect(self.assigned_server, False)
            else:
                print("Processo " + str(self.id) + " deu Erro")
        finally:
            return to_socket

    def close(self):
        self.connection.close()

def main():
    #open('cs.txt', 'w').close()
    arguments = get_parser().parse_args()
    p_counts = arguments.num_processos
    clients = []
    cid = 1

    for p in range(p_counts):
        pross = Processo(cid,p_counts)
        clients.append(pross)
        cid = cid + 1

    for c in clients:
        try:
            c.request()
            time.sleep(5)
        except Exception as e:
            print(str(e))


def get_parser():
    parser = argparse.ArgumentParser(description='Processos')
    parser.add_argument('num_processos', type=int)

    return parser


if __name__ == "__main__":
    main()
