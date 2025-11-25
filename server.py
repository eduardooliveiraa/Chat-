import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000
clients = {}
lock = threading.Lock()

def broadcast(message, sender_conn=None):
    with lock:
        for conn in clients:
            if conn != sender_conn:
                try:
                    conn.send(message.encode())
                except:
                    conn.close()

def handle_client(conn, addr):
    try:
        conn.send("Nickname: ".encode())
        nickname = conn.recv(1024).decode().strip()

        with lock:
            clients[conn] = nickname
        broadcast(f"[Sistema] {nickname} entrou no chat!", conn)

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            if msg.lower() == "/sair":
                break
            timestamp = datetime.now().strftime("%H:%M:%S")
            broadcast(f"[{timestamp}] {nickname}: {msg}", conn)
    except:
        pass
    finally:
        with lock:
            if conn in clients:
                nickname = clients.pop(conn)
                broadcast(f"[Sistema] {nickname} saiu do chat!")
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Servidor rodando...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()