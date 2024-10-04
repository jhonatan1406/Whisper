import socket
import threading
import time

def receber_mensagens(cliente_socket):
    while True:
        try:
            # Receber mensagem do servidor
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            if mensagem:
                print(f"\n{mensagem}")
        except:
            # Fechar conexão se houver erro
            print("Cliente foi desconectado do servidor.")
            cliente_socket.close()
            break

def enviar_mensagens(cliente_socket):
    # Solicitar apelido do cliente
    apelido = input("Bem vindo ao Whisper! Digite seu apelido: ")
    # Enviar o apelido ao servidor
    cliente_socket.send(apelido.encode('utf-8'))

    while True:
        time.sleep(1)
        print("\nEscolha uma opção:")
        print("1 - Listar todos usuários ativos")
        print("2 - Enviar mensagem para todos")
        print("3 - Enviar mensagem para uma pessoa específica")
        print("4 - Sair")
        opcao = input("\nDigite sua opção: ")

        if opcao == '1':
            # Solicitar lista de usuários conectados
            cliente_socket.send("/list".encode('utf-8'))
        elif opcao == '2':
            # Enviar mensagem para todos os usuários
            mensagem = input("Digite a mensagem que deseja enviar a todos: ")
            cliente_socket.send(f"/broadcast:{mensagem}".encode('utf-8'))
        elif opcao == '3':
            # Enviar mensagem para uma pessoa específica
            destinatario_mensagem = input("Digite 'apelido:mensagem': ")
            cliente_socket.send(destinatario_mensagem.encode('utf-8'))
        elif opcao == '4':
            # Encerrar conexão
            print("Desconectando...")
            cliente_socket.close()
            break
        else:
            print("Opção inválida. Tente novamente.")

def main():
    # Criar socket do cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 2003
    # Conectar ao servidor
    cliente.connect((host, port))
    
    # Iniciar threads para enviar e receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_receber.start()

    thread_enviar = threading.Thread(target=enviar_mensagens, args=(cliente,))
    thread_enviar.start()

if __name__ == "__main__":
    main()
