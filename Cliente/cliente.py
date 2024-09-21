import socket
import threading

def receber_mensagens(cliente_socket):
    while True:
        try:
            # Receber mensagem do servidor
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            if mensagem:
                print(f"\n{mensagem}")
        except:
            # Fechar conexão se houver erro
            print("Conexão perdida com o servidor.")
            cliente_socket.close()
            break

def enviar_mensagens(cliente_socket):
    # Solicitar apelido do cliente
    apelido = input("Digite seu apelido: ")
    # Enviar o apelido ao servidor
    cliente_socket.send(apelido.encode('utf-8'))

    while True:
        # O cliente pode digitar comandos ou mensagens no formato "apelido_destinatario: mensagem"
        comando = input("\nDigite '/list' para ver usuários conectados ou 'apelido: mensagem' para enviar: ")
        if comando.startswith('/list'):
            # Solicitar lista de usuários
            cliente_socket.send(comando.encode('utf-8'))
        else:
            # Enviar mensagem para outro usuário
            cliente_socket.send(comando.encode('utf-8'))

def main():
    # Criar socket do cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Conectar ao servidor (endereços podem variar)
    cliente.connect(('127.0.0.1', 2003))
    
    # Iniciar threads para enviar e receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_receber.start()

    thread_enviar = threading.Thread(target=enviar_mensagens, args=(cliente,))
    thread_enviar.start()

if __name__ == "__main__":
    main()
