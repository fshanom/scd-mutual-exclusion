# Deve ser multithread
# Uma thread para receber as conexões de novos processos
# Uma thread para executar o algoritmo da exclusão mútua
# Uma thread atendendo o terminal

# Usar uma estrutura de dados de fila para armazenar os pedidos de acesso a região crítica
# Deve ser gerado um log com todas as mensagens recebidas e enviadas
    # Incluindo: INSTANTE DA MENSAGEM | TIPO DA MENSAGEM | PROCESSO ORIGEM OU DESTINO

# Comunicação entre processos usando sockets
# Cada processo tem seu próprio socket, e o coordenador vai ter uma estrutura de dados com esses sockets.
# Usar sockets tipo UDP (Nesse caso o coordenador tem um só socket para todos os processos).

# A thread de interface deve ficar bloqueada, aguardando os comandos do terminal:
    # 1) Imprimir lista de pedidos atual
    # 2) imprimir quantas vezes cada processo foi atendido
    # 3) Encerrar a execução
# As duas threads (interface e a de algoritmo) acessam a mesma fila, então devem ser sincronizadas.

from asyncio import Queue
from datetime import datetime
import json
import logging
import socket
from threading import Thread
import threading
import time
import util

semaphore = threading.Semaphore()

#Arquivo de log
#logging.basicConfig(filename='resultado.txt', filemode='w', level=logging.INFO)

#Carrega as configurações do server
with open("config.json", "r") as configFile:
    config = json.load(configFile)

#Variáveis globais
BUFFER_SIZE = config["buffer_size"]
DELIMITER = config["message_delimiter"]
MSG_TERMINATOR = config["message_terminator"]
DELAY = config["delay"]
REQ = "REQUEST"
GRT = "GRANT"
REL = "RELEASE"

#dicionario para guardar quantas vezes cada processo foi atendido
dictProcessos = {}

#guarda as thread na fila
thread_pool = []

#lock da RC
lock = threading.Lock()

#fila de mensagens
fila = util.Queue()

class ThreadCoordenador(Thread):
    #sobe socket do coordenador na porta port
    def __init__(self, socket, ip, port):
        Thread.__init__(self)
        self.socket = socket
        self.process_id = 0
        self.ip = ip
        self.port = port
        self.send_msg_queue = util.Queue()

    #método que escreve na rc
    def run(self):
        #logging.info("Conectado a " + self.ip + ":" + str(self.port))
        data = ""
        #self.console()
        while True:
            #pega a mensagem do processo
            data = str(data) + str(self.socket.recv(BUFFER_SIZE))
            if data:
                while MSG_TERMINATOR in data:
                    pos = data.find(MSG_TERMINATOR)
                    msg = data[:pos]
                    data = data[pos+1:]

                    #abrir o arquivo de log em modo append
                    #obtem a hora atual
                    datahora = msg.split(DELIMITER)[0]
                    #print(datahora)

                    #escreve o id e a hora atual no final do arquivo

                    if "PID" in msg:
                        self.process_id = msg.split(":")[1]
                    if REQ in msg or REL in msg:
                        self.send_msg_queue.push(msg)

                        log = open("resultado.txt", "a")
                        now = datetime.utcnow()
                        current_time = now.strftime("%H:%M:%S.%f")
                        data =  data.replace("'", "")
                        log.write(current_time + " | GRANT | Processo " + data + " | Teste \n")
                        log.close()
                        fila.push(data)

                        #adiciona processo no dicionario que registra quantas vezes cada processo foi atendido
                        processo = {'Processo '+data:0}
                        dictProcessos.update(processo) 

                        self.escreveRC(fila)

                    if GRT in msg:
                        with lock:
                            time.sleep(DELAY)
                            self.forward_reply_message(msg)

    def escreveRC(self, pros):

        #for thread in thread_pool:
            #if int(self.process_id) != int(thread.process_id):
        while not pros.isEmpty():

                message = pros.pop()
                #print(message + " está mandando mensagem")
                now = datetime.utcnow()
                current_time = now.strftime("%H:%M:%S.%f")
                semaphore.acquire()
                #thread.socket.send(message + MSG_TERMINATOR)
                log = open("resultado.txt", "a")
                now = datetime.utcnow()
                current_time = now.strftime("%H:%M:%S.%f")
                log.write(current_time + " | RELEASE | Processo " + message + " | Teste \n")
                log.close()
                semaphore.release()

                #atualiza contador
                key = 'Processo ' + message
                if key in dictProcessos:
                    dictProcessos[key] += 1

    def forward_reply_message(self, message):
        pid = int(message.split(DELIMITER)[1])
        #print("Send  msg: " + message + "to " + str(pid))
        for thread in thread_pool:
            #print(thread.process_id + " " + str(pid))
            if int(thread.process_id) == pid:
                semaphore.acquire()
                time.sleep(DELAY)
                thread.socket.send(message + MSG_TERMINATOR)
                time.sleep(DELAY)
                semaphore.release()
    
class ThreadConsole(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        while True:
            print("---------- MENU ----------\n")
            print("1) Imprimir lista de pedidos atual\n")
            print("2) imprimir quantas vezes cada processo foi atendido\n")
            print("3) Encerrar a execução\n")
            print("Digite a opção desejada:")
            op = input()
            
            if(op == '1'):
                print(thread_pool)
            if(op == '2'):
                print(dictProcessos)
            if(op == '3'):
                print("Fim da execução")
                break


if __name__ == "__main__":
    host_IP = config["IP"]
    host_port = config["port"]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_IP, host_port))
    
    #Thread do console
    threadConsole = ThreadConsole()
    threadConsole.start()

    while True:
        server_socket.listen(5)
        (connection_socket, (ip, port)) = server_socket.accept()

        #Thread do coordenador
        threadCoordenador = ThreadCoordenador(connection_socket, ip, port)
        threadCoordenador.start()

        thread_pool.append(threadCoordenador)