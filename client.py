import socket
import os
import tempfile
import vlc
import tkinter as tk
from tkinter import ttk

# Configurações do cliente
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 60000        # Porta usada pelo servidor

class VideoPlayerApp:
    def __init__(self, root, video_path):
        self.root = root
        self.root.title("Player de Vídeo")
        self.video_path = video_path

        # Inicializa o VLC player
        self.player = vlc.MediaPlayer(self.video_path)
        self.player.audio_set_volume(50)  # Volume inicial

        # Cria os botões da interface
        self.create_widgets()

        # Começa a reprodução do vídeo
        self.player.play()

    def create_widgets(self):
        # Criar o título do player
        tk.Label(self.root, text="Player de Vídeo", font=("Arial", 14)).pack(pady=10)

        # Frame para os botões de controle
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Botões de controle
        self.pause_button = ttk.Button(control_frame, text="Pausar/Retomar", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=0, padx=5)
        self.increase_volume_button = ttk.Button(control_frame, text="Aumentar Volume", command=self.increase_volume)
        self.increase_volume_button.grid(row=0, column=1, padx=5)
        self.decrease_volume_button = ttk.Button(control_frame, text="Diminuir Volume", command=self.decrease_volume)
        self.decrease_volume_button.grid(row=0, column=2, padx=5)
        self.quit_button = ttk.Button(control_frame, text="Encerrar", command=self.quit_player)
        self.quit_button.grid(row=0, column=3, padx=5)
        
    def toggle_pause(self):
        """Pausa ou retoma a reprodução do vídeo."""
        self.player.pause()

    def increase_volume(self):
        """Aumenta o volume do player."""
        current_volume = self.player.audio_get_volume()
        new_volume = min(current_volume + 10, 100)  # Limita o volume a 100
        self.player.audio_set_volume(new_volume)
        print(f"Volume aumentado para: {new_volume}%")

    def decrease_volume(self):
        """Diminui o volume do player."""
        current_volume = self.player.audio_get_volume()
        new_volume = max(current_volume - 10, 0)  # Não permite volume menor que 0
        self.player.audio_set_volume(new_volume)
        print(f"Volume reduzido para: {new_volume}%")

    def quit_player(self):
        """Encerra o player e fecha o programa."""
        self.player.stop()
        self.root.destroy()
        os.remove(self.video_path)  # Remove o arquivo temporário
        print("Arquivo temporário removido.")

def main():
    try:
        # Inicializa o socket do cliente
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print(f"Conectado ao servidor em {HOST}:{PORT}.\n")

        # Receber e exibir a lista de vídeos disponíveis
        video_list = client_socket.recv(1024).decode('utf-8')
        print("Vídeos disponíveis:")
        print(video_list)

        # Solicitar o vídeo ao usuário
        video_request = input("Escolha o nome do vídeo para assistir (incluindo .mp4): ").strip()
        client_socket.send(video_request.encode('utf-8'))

        # Verificar a resposta do servidor
        response = client_socket.recv(1024)
        if response == b"200 OK":
            print("Recebendo o vídeo...")

            # Criar um arquivo temporário para salvar o vídeo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                try:
                    while True:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            break
                        temp_video.write(chunk)
                finally:
                    temp_video.close()

            # Iniciar a interface gráfica do player
            root = tk.Tk()
            app = VideoPlayerApp(root, temp_video.name)
            root.mainloop()

        elif response == b"404 NOT FOUND":
            print("Erro: Vídeo não encontrado. Por favor, tente novamente.")
        else:
            print("Erro inesperado do servidor.")

    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor. Certifique-se de que ele está em execução.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        client_socket.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    main()
