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


#Importa bibliotecas
from datetime import datetime
import logging
import socket
import string
import time
from asyncio import Queue
import json
import argparse

#Carrega as configurações do server
with open("config.json", "r") as configFile:
    config = json.load(configFile)

#Incia o socket
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Definição do tamanho da mensagem: 10 bytes da mensagem + 16 que é o tamanho do timestamp
f = 40

#Cria classe do processo
class Processo:
    def __init__(self, processo_id, nom_processo,num_processo):
        self.id = processo_id
        self.connections = []
        self.number_set = []
        self.processo_count = num_processo
        self.number_set_idx = 0
        self.nome = nom_processo
        print("Iniciando Processo "+ self.nome)
        
    
    #Método que solicita o acesso para escrita na Região Critica
    def request(self):
        #Anota no txt o REQUESt 
        log = open("resultado.txt", "a")
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M:%S.%f")
        #Mensagem de request tem identificador 1
        msg = current_time + "|" + str(1) + "|" + self.nome + ' - ' +str(self.id) + "|"
        msg = msg.ljust(f,"0")
        msg = msg + '\n'
        log.write(msg)
        log.close()

        #Realiza a coneção no coordenador
        connection = self.__connect(True)

        #Menssagem que será enviada e envio
        msg = current_time + ' | REQUEST #' + self.nome + ' - ' +str(self.id)
        connection.sendall(msg.encode())
        print('Processo ' + str(self.id) + ' mandou solicitação de escrita Coordenador')
        self.connections.append(connection)
        self.number_set_idx = self.number_set_idx + 1
        time.sleep(3)    

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
    #Fechar processo
    def close(self):
        self.connection.close()

def main():
    #Inicia script com parametro, parametro é a quantidade de processos que serão executados
    arguments = get_parser().parse_args()
    p_counts = arguments.num_processos
    p_nome = arguments.nom_processo
    clients = []
    cid = 1

    #For para incluir os processos numa lista
    for p in range(p_counts):
        pross = Processo(cid,p_nome,p_counts)
        clients.append(pross)
        cid = cid + 1

    #For para executar request de cada cliente da lista
    for c in clients:
        try:
            c.request()
            #time.sleep(5)
        except Exception as e:
            print(str(e))

#Configura argumento do script
def get_parser():
    parser = argparse.ArgumentParser(description='Processos')
    parser.add_argument('nom_processo', type=str)
    parser.add_argument('num_processos', type=int)

    return parser


if __name__ == "__main__":
    main()
