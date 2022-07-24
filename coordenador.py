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

