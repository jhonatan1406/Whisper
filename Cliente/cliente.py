import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import time

# Função para receber mensagens
def receber_mensagens(cliente_socket, janela_chat, lista_usuarios):
    while True:
        try:
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            if mensagem.startswith("Atualmente, há"):  # Atualizar lista de usuários conectados
                usuarios_conectados = mensagem.split(": ")[1]
                lista_usuarios.delete(0, tk.END)
                for usuario in usuarios_conectados.split(", "):
                    lista_usuarios.insert(tk.END, usuario)
            else:
                janela_chat.config(state=tk.NORMAL)
                janela_chat.insert(tk.END, mensagem + "\n")
                janela_chat.config(state=tk.DISABLED)
                janela_chat.yview(tk.END)
        except:
            print("Cliente foi desconectado do servidor.")
            cliente_socket.close()
            break

# Função para enviar mensagens
def enviar_mensagem(cliente_socket, entrada_mensagem, janela_chat, destinatario, label_destinatario):
    mensagem = entrada_mensagem.get()

    if mensagem and destinatario.get():
        cliente_socket.send(f"{destinatario.get()}:{mensagem}".encode('utf-8'))
        entrada_mensagem.delete(0, tk.END)
        janela_chat.config(state=tk.NORMAL)
        janela_chat.insert(tk.END, f"Você para {destinatario.get()}: {mensagem}\n")
        janela_chat.config(state=tk.DISABLED)
        janela_chat.yview(tk.END)
        label_destinatario.config(text=f"Enviando mensagem para: {destinatario.get()}")
    else:
        messagebox.showwarning("Atenção", "Selecione um destinatário antes de enviar a mensagem.")

# Função para enviar mensagem a todos
def enviar_para_todos(cliente_socket, entrada_mensagem, janela_chat, label_destinatario):
    mensagem = entrada_mensagem.get()
    if mensagem:
        cliente_socket.send(f"/broadcast:{mensagem}".encode('utf-8'))
        entrada_mensagem.delete(0, tk.END)
        janela_chat.config(state=tk.NORMAL)
        janela_chat.insert(tk.END, f"Você (para todos): {mensagem}\n")
        janela_chat.config(state=tk.DISABLED)
        janela_chat.yview(tk.END)
        label_destinatario.config(text="Enviando mensagem para: Todos os usuários")

# Função para atualizar lista de usuários conectados a cada 1 segundos
def atualizar_lista_usuarios(cliente_socket):
    while True:
        time.sleep(1)  # Atualizar a lista a cada 1 segundos
        cliente_socket.send("/list".encode('utf-8'))

# Função para atualizar destinatário ao selecionar um usuário na lista
def atualizar_destinatario(event, lista_usuarios, destinatario, label_destinatario):
    try:
        selecionado = lista_usuarios.get(lista_usuarios.curselection())
        destinatario.set(selecionado)
        label_destinatario.config(text=f"Enviando mensagem para: {selecionado}")
    except tk.TclError:
        pass

# Função para capturar 'Enter' no campo de mensagem e enviar automaticamente
def enviar_ao_teclar_enter(event, cliente_socket, entrada_mensagem, janela_chat, destinatario, label_destinatario):
    enviar_mensagem(cliente_socket, entrada_mensagem, janela_chat, destinatario, label_destinatario)

# Função para estilizar e iniciar a interface gráfica
def iniciar_interface(cliente_socket):
    janela = tk.Tk()
    janela.title("Whisper - Cliente")
    janela.configure(bg="#282C34")

    # Divisão principal da janela
    frame_principal = tk.Frame(janela, bg="#282C34")
    frame_principal.pack(padx=10, pady=10)

    # Chat
    janela_chat = scrolledtext.ScrolledText(frame_principal, wrap=tk.WORD, height=15, width=50, bg="#1C1E24", fg="#FFFFFF", insertbackground="white")
    janela_chat.grid(row=0, column=0, padx=10, pady=10)
    janela_chat.config(state=tk.DISABLED)

    # Lista de usuários conectados
    lista_usuarios = tk.Listbox(frame_principal, height=15, selectmode=tk.SINGLE, bg="#1C1E24", fg="#61AFEF")
    lista_usuarios.grid(row=0, column=1, padx=10, pady=10)

    # Variável para armazenar o destinatário selecionado
    destinatario = tk.StringVar()

    # Rótulo para exibir o destinatário selecionado
    label_destinatario = tk.Label(frame_principal, text="Enviando mensagem para: Nenhum", fg="#61AFEF", bg="#282C34", font=("Arial", 10, "bold"))
    label_destinatario.grid(row=1, column=0, padx=10, pady=5)

    # Entrada de mensagem
    entrada_mensagem = tk.Entry(frame_principal, width=50, bg="#1C1E24", fg="#ABB2BF", insertbackground="white")
    entrada_mensagem.grid(row=2, column=0, padx=10, pady=10)
    entrada_mensagem.bind("<Return>", lambda event: enviar_ao_teclar_enter(event, cliente_socket, entrada_mensagem, janela_chat, destinatario, label_destinatario))

    # Botão enviar
    botao_enviar = tk.Button(frame_principal, text="Enviar", bg="#61AFEF", fg="#282C34", command=lambda: enviar_mensagem(cliente_socket, entrada_mensagem, janela_chat, destinatario, label_destinatario))
    botao_enviar.grid(row=2, column=1, pady=5)

    # Botão enviar para todos
    botao_enviar_todos = tk.Button(frame_principal, text="Enviar para Todos", bg="#61AFEF", fg="#282C34", command=lambda: enviar_para_todos(cliente_socket, entrada_mensagem, janela_chat, label_destinatario))
    botao_enviar_todos.grid(row=3, column=1, pady=5)

    # Bind para atualizar o destinatário ao clicar em um usuário
    lista_usuarios.bind('<<ListboxSelect>>', lambda event: atualizar_destinatario(event, lista_usuarios, destinatario, label_destinatario))

    # Thread para receber mensagens do servidor
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente_socket, janela_chat, lista_usuarios))
    thread_receber.start()

    # Thread para atualizar lista de usuários automaticamente
    thread_atualizar_lista = threading.Thread(target=atualizar_lista_usuarios, args=(cliente_socket,))
    thread_atualizar_lista.daemon = True  # Daemon para parar quando o programa fechar
    thread_atualizar_lista.start()

    janela.mainloop()

# Função para exibir a tela de entrada do apelido
def solicitar_apelido(cliente_socket):
    janela_apelido = tk.Tk()
    janela_apelido.title("Bem-vindo ao Whisper!")
    janela_apelido.configure(bg="#282C34")

    mensagem_bem_vindo = tk.Label(janela_apelido, text="Bem-vindo ao Whisper!\nUm lugar seguro para conversar.", fg="#61AFEF", bg="#282C34", font=("Arial", 14, "bold"))
    mensagem_bem_vindo.pack(padx=20, pady=20)

    apelido_label = tk.Label(janela_apelido, text="Digite seu apelido:", fg="#ABB2BF", bg="#282C34", font=("Arial", 10))
    apelido_label.pack(pady=5)

    apelido_entry = tk.Entry(janela_apelido, width=30, bg="#1C1E24", fg="#FFFFFF", insertbackground="white")
    apelido_entry.pack(pady=10)

    def confirmar_apelido():
        apelido = apelido_entry.get()
        if apelido:
            cliente_socket.send(apelido.encode('utf-8'))
            janela_apelido.destroy()
            iniciar_interface(cliente_socket)
        else:
            messagebox.showwarning("Atenção", "Por favor, insira um apelido válido.")

    botao_confirmar = tk.Button(janela_apelido, text="Entrar", bg="#61AFEF", fg="#282C34", command=confirmar_apelido)
    botao_confirmar.pack(pady=10)

    janela_apelido.mainloop()

# Função principal
def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 2003
    cliente.connect((host, port))

    solicitar_apelido(cliente)

if __name__ == "__main__":
    main()
