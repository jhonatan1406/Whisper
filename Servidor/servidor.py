import socket
import threading

# Dicionário para armazenar usuários conectados (apelido: socket)
clientes_conectados = {}

# Função para gerenciar o cliente
def handle_cliente(cliente_socket, apelido):
    while True:
        try:
            # Receber mensagem do cliente
            msg = cliente_socket.recv(1024).decode('utf-8')
            if not msg:
                break

            if msg.startswith('/list'):
                # Enviar a lista de usuários conectados
                lista_usuarios = "Usuários conectados: " + ", ".join(clientes_conectados.keys())
                cliente_socket.send(lista_usuarios.encode('utf-8'))
            elif msg.startswith('/broadcast:'):
                # Enviar mensagem para todos os usuários conectados
                mensagem = msg.split(":", 1)[1]
                for usuario, socket_usuario in clientes_conectados.items():
                    if socket_usuario != cliente_socket:
                        socket_usuario.send(f"De {apelido}: {mensagem}".encode('utf-8'))
            else:
                # A mensagem deve seguir o formato "apelido_destinatario: mensagem"
                if ':' in msg:
                    apelido_destinatario, mensagem = msg.split(':', 1)
                    if apelido_destinatario in clientes_conectados:
                        destinatario_socket = clientes_conectados[apelido_destinatario]
                        try:
                            destinatario_socket.send(f"De {apelido}: {mensagem}".encode('utf-8'))
                        except Exception as e:
                            print(f"Erro ao enviar mensagem ao destinatário {apelido_destinatario}: {e}")
                            break
                    else:
                        cliente_socket.send(f"Usuário {apelido_destinatario} não encontrado.".encode('utf-8'))
                else:
                    cliente_socket.send("Formato inválido. Use 'apelido: mensagem'.".encode('utf-8'))
        except Exception as e:
            print(f"Erro inesperado para {apelido}: {e}")
            break

    # Remover cliente da lista de conectados ao desconectar
    if apelido in clientes_conectados:
        del clientes_conectados[apelido]
    cliente_socket.close()
    print(f"{apelido} desconectado.")

def main():
    # Criar socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 2003
    servidor.bind((host, port))
    servidor.listen(5)
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
