import socket
import os

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 60000        # Porta usada pelo servidor
VIDEO_DIR = "videos"  # Diretório onde os vídeos estão armazenados

# Inicializa o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Servidor iniciado em {HOST}:{PORT}. Aguardando conexões...")

while True:
    conn, addr = server_socket.accept()
    print(f"Conexão recebida de {addr}")

    # Enviar a lista de vídeos disponíveis
    videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    conn.send("\n".join(videos).encode('utf-8'))

    # Receber o nome do vídeo escolhido pelo cliente
    video_request = conn.recv(1024).decode('utf-8')
    video_path = os.path.join(VIDEO_DIR, video_request)

    if os.path.exists(video_path):
        conn.send(b"200 OK")
        print(f"Iniciando streaming do vídeo: {video_request}")

        # Enviar o vídeo em chunks (streaming)
        with open(video_path, 'rb') as video_file:
            chunk = video_file.read(1024)
            while chunk:
                conn.send(chunk)
                chunk = video_file.read(1024)
        print(f"Streaming do vídeo '{video_request}' concluído!")
    else:
        conn.send(b"404 NOT FOUND")
        print(f"Vídeo '{video_request}' não encontrado.")

    conn.close()
