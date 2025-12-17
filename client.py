import socket
import threading
import tkinter as tk
from tkinter import simpledialog, ttk
from datetime import datetime
import re
from cryptography.fernet import Fernet
import base64
import os
import time

HOST = "127.0.0.1"
PORT = 3000

print("=== INICIANDO CLIENTE DE CHAT ===")

# Configuração de criptografia
def setup_encryption():
    """Configura a criptografia com fallback"""
    key_file = 'server.key'
    
    if os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            cipher = Fernet(key)
            print("✓ Criptografia ativada - chave carregada")
            return cipher, True
        except Exception as e:
            print(f"Erro ao carregar chave: {e}")
    
    print("AVISO: Modo não criptografado (server.key não encontrado)")
    return None, False

# Inicializa criptografia
cipher, encryption_enabled = setup_encryption()

def encrypt_message(message):
    """Criptografa uma mensagem se disponível"""
    if cipher and encryption_enabled:
        try:
            return cipher.encrypt(message.encode()).decode()
        except Exception as e:
            print(f"Erro ao criptografar: {e}")
    return message

def decrypt_message(encrypted_message):
    """Descriptografa uma mensagem se disponível"""
    if cipher and encryption_enabled:
        try:
            return cipher.decrypt(encrypted_message.encode()).decode()
        except Exception as e:
            print(f"Erro ao descriptografar: {e}")
            return encrypted_message
    return encrypted_message

# Conexão
try:
    print(f"🔗 Conectando ao servidor {HOST}:{PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.setblocking(True)
    print("✅ Conectado ao servidor!")
    
except ConnectionRefusedError:
    print("❌ ERRO: Servidor não encontrado!")
    print("   Certifique-se de que o servidor está rodando:")
    print("   - Execute: python3 server.py")
    print("   - Verifique se a porta 5000 está livre")
    exit(1)
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    exit(1)

# Interface gráfica
root = tk.Tk()
root.title("Chat Criptografado" if encryption_enabled else "Chat")
root.configure(bg="#1e1e1e")
root.geometry("900x600")
root.minsize(400, 500)

# Variáveis globais
nickname = "Anon"
user_count = 1
MAX_BUBBLE_WIDTH = 500
BUBBLE_PADX = 16
BUBBLE_PADY = 10

# Rate limiting para typing
last_typing_sent = 0
TYPING_COOLDOWN = 2  # segundos

# Flag para controlar handshake
handshake_complete = False

# Configuração de estilo
style = ttk.Style()
style.theme_use('clam')

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#007acc", foreground="white", borderwidth=0, focuscolor="none")
style.map("TButton", background=[("active", "#005a9e")])

# Container principal
main_container = ttk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Cabeçalho
header_frame = ttk.Frame(main_container)
header_frame.pack(fill=tk.X, pady=(0, 10))

title_frame = ttk.Frame(header_frame)
title_frame.pack(fill=tk.X)

status_color = "#4CAF50" if encryption_enabled else "#FF9800"
status_text = "● Criptografado" if encryption_enabled else "● Não Criptografado"

app_title = tk.Label(title_frame, text="Chat Criptografado" if encryption_enabled else "Chat", 
                    bg="#1e1e1e", fg="white", 
                    font=("Segoe UI", 16, "bold"))
app_title.pack(side=tk.LEFT)

status_frame = ttk.Frame(header_frame)
status_frame.pack(fill=tk.X, pady=5)

connection_status = tk.Label(status_frame, text=status_text, 
                           bg="#1e1e1e", fg=status_color, 
                           font=("Segoe UI", 10))
connection_status.pack(side=tk.LEFT)

user_count_label = tk.Label(status_frame, text="1 usuário online", 
                          bg="#1e1e1e", fg="#888", 
                          font=("Segoe UI", 10))
user_count_label.pack(side=tk.RIGHT)

# Área de mensagens
chat_container = ttk.Frame(main_container)
chat_container.pack(fill=tk.BOTH, expand=True)

messages_border_frame = ttk.Frame(chat_container, relief="solid", borderwidth=1)
messages_border_frame.pack(fill=tk.BOTH, expand=True)

canvas_frame = ttk.Frame(messages_border_frame)
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

canvas = tk.Canvas(canvas_frame, bg="#252526", highlightthickness=0, relief="flat")
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
messages_frame = ttk.Frame(canvas, style="TFrame")

messages_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=messages_frame, anchor="nw", width=canvas.winfo_width())
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def configure_canvas_width(event):
    canvas.itemconfig("all", width=event.width)
canvas.bind("<Configure>", configure_canvas_width)

# Área de input
input_container = ttk.Frame(main_container)
input_container.pack(fill=tk.X, pady=(10, 0))

input_frame = ttk.Frame(input_container)
input_frame.pack(fill=tk.X)

entry_style = ttk.Style()
entry_style.configure("Modern.TEntry", 
                     fieldbackground="#333", 
                     foreground="white", 
                     borderwidth=2, 
                     relief="flat",
                     padding=(10, 8))

entry_msg = ttk.Entry(input_frame, style="Modern.TEntry", font=("Segoe UI", 11))
entry_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

# Botão de emojis
def create_emoji_picker():
    """Cria seletor de emojis"""
    if not handshake_complete:
        return
        
    emoji_window = tk.Toplevel(root)
    emoji_window.title("Emojis")
    emoji_window.geometry("300x200")
    emoji_window.configure(bg="#2d2d30")
    
    emojis = ["😊", "😎", "🎉", "👍", "👎", "❤️", "🔥", "✨", "🚀", "💡"]
    
    emoji_frame = ttk.Frame(emoji_window)
    emoji_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    for i, emoji in enumerate(emojis):
        btn = tk.Button(emoji_frame, text=emoji, font=("Segoe UI", 14),
                       command=lambda e=emoji: insert_emoji(e),
                       bg="#444", fg="white", relief="flat")
        btn.grid(row=i//5, column=i%5, padx=2, pady=2)
    
    def insert_emoji(emoji):
        entry_msg.insert(tk.END, emoji)
        emoji_window.destroy()
    
    close_btn = ttk.Button(emoji_window, text="Fechar", command=emoji_window.destroy)
    close_btn.pack(pady=5)

emoji_btn = ttk.Button(input_frame, text="😊", width=3, command=create_emoji_picker)
emoji_btn.pack(side=tk.LEFT, padx=(0, 10))

# Botão enviar
btn_send = ttk.Button(input_frame, text="Enviar", command=lambda: send_message(), 
                     style="TButton", width=10)
btn_send.pack(side=tk.RIGHT, padx=(10, 0))

# ========== FUNÇÕES DE MENSAGENS ==========
def update_user_count(count):
    global user_count
    user_count = count
    if count == 1:
        user_count_label.config(text="1 usuário online")
    else:
        user_count_label.config(text=f"{count} usuários online")

def extract_user_count(text):
    patterns = [
        r'(\d+)\s*usuários',
        r'(\d+)\s*users',
        r'(\d+)\s*online',
        r'usuários:\s*(\d+)',
        r'users:\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    if "entrou" in text.lower():
        return user_count + 1
    elif "saiu" in text.lower():
        return max(1, user_count - 1)
    
    return user_count

def add_system_message(text):
    wrapper = ttk.Frame(messages_frame, style="TFrame")
    wrapper.pack(fill=tk.X, pady=8)
    
    new_count = extract_user_count(text)
    update_user_count(new_count)
    
    display_text = text
    if any(word in text.lower() for word in ['usuários', 'users', 'online']):
        display_text = re.sub(r'\d+\s*usuários?\s*', '', text, flags=re.IGNORECASE)
        display_text = re.sub(r'\s*—.*$', '', display_text).strip()
    
    lbl = tk.Label(wrapper, text=display_text, 
                   bg="#2d2d30", fg="#ce9178", 
                   font=("Segoe UI", 10, "italic"),
                   wraplength=MAX_BUBBLE_WIDTH, 
                   justify="center", 
                   padx=12, pady=6,
                   relief="flat")
    lbl.pack(anchor="center")
    
    canvas.yview_moveto(1.0)
    root.update_idletasks()

def add_rich_message(author, text, timestamp=None, sent=False, message_type="normal"):
    """Adiciona mensagem com formatação rica"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    message_container = ttk.Frame(messages_frame, style="TFrame")
    message_container.pack(fill=tk.X, pady=2, padx=10)
    
    # Cores baseadas no tipo de mensagem
    colors = {
        "normal": {"bg": "#2d2d30", "header": "#888"},
        "system": {"bg": "#0d3d5a", "header": "#4CAF50"},
        "private": {"bg": "#5a2d5a", "header": "#E91E63"},
        "warning": {"bg": "#5a2d2d", "header": "#FF5722"},
        "you": {"bg": "#005a9e", "header": "#007acc"}
    }
    
    color_set = colors["you"] if sent else colors.get(message_type, colors["normal"])
    
    alignment = "e" if sent else "w"
    
    inner_frame = ttk.Frame(message_container, style="TFrame")
    inner_frame.pack(fill=tk.X, anchor=alignment)
    
    # Header
    header_text = f"Você • {timestamp}" if sent else f"{author} • {timestamp}"
    
    header_label = tk.Label(inner_frame, text=header_text,
                          bg="#1e1e1e", fg=color_set["header"],
                          font=("Segoe UI", 9, "bold"))
    header_label.pack(anchor=alignment)
    
    # Bubble de mensagem
    bubble = tk.Label(inner_frame, text=text,
                     bg=color_set["bg"], fg="white",
                     font=("Segoe UI", 10),
                     wraplength=MAX_BUBBLE_WIDTH,
                     justify="left",
                     padx=BUBBLE_PADX, pady=BUBBLE_PADY,
                     relief="flat")
    bubble.pack(anchor=alignment, pady=(2, 0))
    
    canvas.yview_moveto(1.0)
    root.update_idletasks()

def add_typing_indicator(user):
    """Mostra indicador de digitação"""
    typing_label = tk.Label(messages_frame, text=f"{user} está digitando...",
                           bg="#1e1e1e", fg="#888", font=("Segoe UI", 9, "italic"))
    typing_label.pack(anchor="w", padx=10, pady=2)
    
    def remove_indicator():
        if typing_label.winfo_exists():
            typing_label.destroy()
    
    root.after(3000, remove_indicator)
    canvas.yview_moveto(1.0)

# ========== FUNÇÕES DE COMUNICAÇÃO ==========
def send_typing_indicator():
    """Envia indicador de digitação (NÃO criptografa)"""
    global last_typing_sent
    
    if not handshake_complete:
        return
        
    current_time = time.time()
    if current_time - last_typing_sent < TYPING_COOLDOWN:
        return
    
    last_typing_sent = current_time
    
    try:
        sock.send("\\typing".encode())
    except:
        pass

def on_key_press(event):
    """Detecta quando usuário está digitando"""
    if not handshake_complete:
        return
        
    if event.keysym in ['Return', 'BackSpace', 'Delete', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
        return
    
    send_typing_indicator()

def send_message(event=None):
    """Envia mensagem"""
    if not handshake_complete:
        return
        
    msg = entry_msg.get().strip()
    if not msg:
        return
    
    # Criptografa antes de enviar
    encrypted_msg = encrypt_message(msg)
    
    try:
        sock.send(encrypted_msg.encode())
    except Exception as e:
        add_rich_message("Sistema", "[Sistema] Erro ao enviar — conexão perdida.", message_type="warning")
        connection_status.config(text="● Desconectado", fg="#f44336")
        return

    # Mostra localmente
    add_rich_message(nickname, msg, timestamp=datetime.now().strftime("%H:%M"), sent=True)
    entry_msg.delete(0, tk.END)

    if msg.lower() == "/sair":
        try:
            sock.close()
        except:
            pass
        root.after(200, root.destroy())

def safe_ask_nickname():
    """Solicita nickname de forma segura"""
    try:
        nickname_input = simpledialog.askstring("Nickname", "Digite seu nickname:", parent=root)
        if not nickname_input or nickname_input.strip() == "":
            return "Anon"
        return nickname_input.strip()
    except Exception as e:
        print(f"Erro ao solicitar nickname: {e}")
        return "Anon"

def receive_messages():
    """Recebe e processa mensagens do servidor"""
    global handshake_complete, nickname
    
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            
            raw_message = data.decode()
            
            # Handshake: Nickname request
            if raw_message == "NICKNAME_REQUEST":
                nickname = safe_ask_nickname()
                sock.send(nickname.encode())
                continue
                
            # Handshake: Welcome
            elif raw_message == "WELCOME":
                handshake_complete = True
                root.after(0, lambda: add_rich_message("Sistema", f"[Sistema] Bem-vindo(a), {nickname}! Conexão estabelecida.", message_type="system"))
                continue
            
            # Handshake: Error
            elif raw_message.startswith("ERROR:"):
                error_msg = raw_message.replace("ERROR:", "")
                root.after(0, lambda: add_rich_message("Sistema", f"[Sistema] Erro: {error_msg}", message_type="warning"))
                continue
            
            # Mensagem de typing
            if "está digitando..." in raw_message:
                user = raw_message.replace("[Sistema]", "").replace("está digitando...", "").strip()
                root.after(0, lambda: add_typing_indicator(user))
                continue
            
            # Mensagens normais (criptografadas)
            decrypted_msg = decrypt_message(raw_message)
            
            # Processa no thread principal do Tkinter
            if decrypted_msg.startswith("[Sistema]"):
                root.after(0, lambda: add_rich_message("Sistema", decrypted_msg, message_type="system"))
            
            elif decrypted_msg.startswith("[Privado]"):
                root.after(0, lambda: add_rich_message("Privado", decrypted_msg, message_type="private"))
            
            else:
                # Mensagem normal
                try:
                    if decrypted_msg.startswith("[") and "]" in decrypted_msg:
                        ts_end = decrypted_msg.find("]")
                        timestamp = decrypted_msg[1:ts_end]
                        rest = decrypted_msg[ts_end+2:]
                        if ":" in rest:
                            nick_end = rest.find(":")
                            nick = rest[:nick_end].strip()
                            text = rest[nick_end+1:].strip()
                            root.after(0, lambda: add_rich_message(nick, text, timestamp=timestamp, sent=False))
                        else:
                            root.after(0, lambda: add_rich_message("Anon", decrypted_msg, sent=False))
                    else:
                        root.after(0, lambda: add_rich_message("Anon", decrypted_msg, sent=False))
                except Exception as e:
                    root.after(0, lambda: add_rich_message("Anon", decrypted_msg, sent=False))
                    
    except Exception as e:
        print(f"Erro na recepção: {e}")
        root.after(0, lambda: connection_status.config(text="● Desconectado", fg="#f44336"))
        root.after(0, lambda: add_rich_message("Sistema", "[Sistema] Conexão com o servidor perdida", message_type="warning"))

def on_closing():
    """Fecha a conexão ao sair"""
    try:
        if handshake_complete:
            sock.send(encrypt_message("/sair").encode())
    except:
        pass
    finally:
        root.destroy()

# ========== CONFIGURAÇÃO DE EVENTOS ==========
root.protocol("WM_DELETE_WINDOW", on_closing)

def show_tooltip(event):
    if not handshake_complete:
        return
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
    label = tk.Label(tooltip, text="Enviar mensagem (Ctrl+Enter)", 
                    background="#ffffe0", relief="solid", borderwidth=1)
    label.pack()
    tooltip.after(3000, tooltip.destroy())

btn_send.bind("<Enter>", show_tooltip)

def ctrl_enter_send(event):
    if handshake_complete:
        send_message()
root.bind('<Control-Return>', ctrl_enter_send)

# Bind para detectar digitação
entry_msg.bind("<KeyPress>", on_key_press)
entry_msg.bind("<Return>", send_message)

# ========== INICIALIZAÇÃO ==========
# Inicia thread para receber mensagens
t = threading.Thread(target=receive_messages, daemon=True)
t.start()

# Desabilita input até handshake completar
entry_msg.config(state='disabled')
btn_send.config(state='disabled')
emoji_btn.config(state='disabled')

def enable_chat():
    """Habilita o chat após handshake"""
    entry_msg.config(state='normal')
    btn_send.config(state='normal')
    emoji_btn.config(state='normal')
    entry_msg.focus()

# Verifica periodicamente se handshake foi completado
def check_handshake():
    if handshake_complete:
        root.after(0, enable_chat)
    else:
        root.after(100, check_handshake)

root.after(100, check_handshake)

# Centraliza janela
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

add_rich_message("Sistema", "[Sistema] Conectando ao servidor...", message_type="system")

root.mainloop()