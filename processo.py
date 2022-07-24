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