import socket
import threading

# Dicionário para armazenar usuários conectados (apelido: endereço)
clientes_conectados = {}

# Função para gerenciar o cliente
def handle_cliente(cliente_socket, apelido):
    while True:
        try:
            # Receber mensagem do cliente
            msg = cliente_socket.recv(1024).decode('utf-8')
            if msg.startswith('/list'):
                # Enviar a lista de usuários conectados
                lista_usuarios = "Usuários conectados: " + ", ".join(clientes_conectados.keys())
                cliente_socket.send(lista_usuarios.encode('utf-8'))
            else:
                # A mensagem deve seguir o formato "apelido_destinatario: mensagem"
                apelido_destinatario, mensagem = msg.split(':', 1)
                # Enviar mensagem ao destinatário
                if apelido_destinatario in clientes_conectados:
                    destinatario_socket = clientes_conectados[apelido_destinatario]
                    try:
                        destinatario_socket.send(f"De {apelido}: {mensagem}".encode('utf-8'))
                    except:
                        destinatario_socket.close()
                        del clientes_conectados[apelido_destinatario]
                else:
                    cliente_socket.send(f"Usuário {apelido_destinatario} não encontrado.".encode('utf-8'))
        except:
            # Remover cliente da lista de conectados ao desconectar
            del clientes_conectados[apelido]
            cliente_socket.close()
            print(f"{apelido} desconectado.")
            break

def main():
    # Criar socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Porta de conexão (ex: 2003)
    servidor.bind(('0.0.0.0', 2003))
    
    # Habilitar o servidor para aceitar conexões
    servidor.listen()
    print("Servidor aguardando conexões...")

    while True:
        # Aceitar conexão de um cliente
        cliente_socket, cliente_endereco = servidor.accept()
        print(f"Nova conexão de {cliente_endereco}")
        
        # Solicitar apelido do cliente
        cliente_socket.send("Digite seu apelido: ".encode('utf-8'))
        apelido = cliente_socket.recv(1024).decode('utf-8')
        clientes_conectados[apelido] = cliente_socket
        print(f"{apelido} conectado.")

        # Iniciar uma nova thread para gerenciar o cliente conectado
        thread = threading.Thread(target=handle_cliente, args=(cliente_socket, apelido))
        thread.start()

if __name__ == "__main__":
    main()
