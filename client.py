import socket
import threading
import tkinter as tk
from tkinter import simpledialog, ttk
from datetime import datetime
import re

HOST = "127.0.0.1"  # ajuste se for rodar em outra máquina
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.setblocking(True)

root = tk.Tk()
root.title("Chat")
root.configure(bg="#1e1e1e")
root.geometry("900x600")
root.minsize(400, 500)

style = ttk.Style()
style.theme_use('clam')

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#007acc", foreground="white", borderwidth=0, focuscolor="none")
style.map("TButton", background=[("active", "#005a9e")])

main_container = ttk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

header_frame = ttk.Frame(main_container)
header_frame.pack(fill=tk.X, pady=(0, 10))

title_frame = ttk.Frame(header_frame)
title_frame.pack(fill=tk.X)

app_title = tk.Label(title_frame, text="Chat", 
                    bg="#1e1e1e", fg="white", 
                    font=("Segoe UI", 16, "bold"))
app_title.pack(side=tk.LEFT)

status_frame = ttk.Frame(header_frame)
status_frame.pack(fill=tk.X, pady=5)

connection_status = tk.Label(status_frame, text="● Conectado", 
                           bg="#1e1e1e", fg="#4CAF50", 
                           font=("Segoe UI", 10))
connection_status.pack(side=tk.LEFT)

user_count_label = tk.Label(status_frame, text="1 usuário online", 
                          bg="#1e1e1e", fg="#888", 
                          font=("Segoe UI", 10))
user_count_label.pack(side=tk.RIGHT)

chat_container = ttk.Frame(main_container)
chat_container.pack(fill=tk.BOTH, expand=True)

messages_border_frame = ttk.Frame(chat_container, relief="solid", borderwidth=1)
messages_border_frame.pack(fill=tk.BOTH, expand=True)

canvas_frame = ttk.Frame(messages_border_frame)
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

canvas = tk.Canvas(canvas_frame, bg="#252526", highlightthickness=0, relief="flat")
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
messages_frame = ttk.Frame(canvas, style="TFrame")

messages_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=messages_frame, anchor="nw", width=canvas.winfo_width())
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def configure_canvas_width(event):
    canvas.itemconfig("all", width=event.width)
canvas.bind("<Configure>", configure_canvas_width)

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

btn_send = ttk.Button(input_frame, text="Enviar", command=lambda: send_message(), 
                     style="TButton", width=10)
btn_send.pack(side=tk.RIGHT, padx=(10, 0))


user_count = 1

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

MAX_BUBBLE_WIDTH = 500
BUBBLE_PADX = 16
BUBBLE_PADY = 10

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

def add_message(author, text, timestamp=None, sent=False):
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    message_container = ttk.Frame(messages_frame, style="TFrame")
    message_container.pack(fill=tk.X, pady=4, padx=10)
    
    alignment = "e" if sent else "w"
    
    inner_frame = ttk.Frame(message_container, style="TFrame")
    inner_frame.pack(fill=tk.X, anchor=alignment)
    
    if sent:
        bubble_bg = "#005a9e"  
        header_color = "#007acc"
    else:
        bubble_bg = "#2d2d30"  
        header_color = "#888"
    
    header_text = f"Você • {timestamp}" if sent else f"{author} • {timestamp}"
    header_label = tk.Label(inner_frame, text=header_text,
                          bg="#1e1e1e", fg=header_color,
                          font=("Segoe UI", 9))
    header_label.pack(anchor=alignment)
    
    bubble = tk.Label(inner_frame, text=text,
                     bg=bubble_bg, fg="white",
                     font=("Segoe UI", 10),
                     wraplength=MAX_BUBBLE_WIDTH,
                     justify="left",
                     padx=BUBBLE_PADX, pady=BUBBLE_PADY,
                     relief="flat")
    bubble.pack(anchor=alignment, pady=(2, 0))
    
    canvas.yview_moveto(1.0)
    root.update_idletasks()

def receive_messages():
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            msg = data.decode(errors="ignore")
            
            if msg.startswith("[Sistema]"):
                add_system_message(msg)
            else:
                try:
                    if msg.startswith("[") and "]" in msg:
                        ts_end = msg.find("]")
                        timestamp = msg[1:ts_end]
                        rest = msg[ts_end+2:]
                        if ":" in rest:
                            nick_end = rest.find(":")
                            nick = rest[:nick_end].strip()
                            text = rest[nick_end+1:].strip()
                            add_message(nick, text, timestamp=timestamp, sent=False)
                        else:
                            add_message("Anon", msg, sent=False)
                    else:
                        add_message("Anon", msg, sent=False)
                except Exception:
                    add_message("Anon", msg, sent=False)
    except Exception:
        connection_status.config(text="● Desconectado", fg="#f44336")
        add_system_message("[Sistema] Conexão com o servidor perdida")
    finally:
        try:
            sock.close()
        except:
            pass

def send_message(event=None):
    msg = entry_msg.get().strip()
    if not msg:
        return
    
    try:
        sock.send(msg.encode())
    except Exception:
        add_system_message("[Sistema] Erro ao enviar — conexão perdida.")
        connection_status.config(text="● Desconectado", fg="#f44336")
        return

    add_message(nickname, msg, timestamp=datetime.now().strftime("%H:%M"), sent=True)
    entry_msg.delete(0, tk.END)

    if msg.lower() == "/sair":
        try:
            sock.close()
        except:
            pass
        root.after(200, root.destroy)

def on_closing():
    try:
        sock.send("/sair".encode())
    except:
        pass
    finally:
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

def show_tooltip(event):
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
    label = tk.Label(tooltip, text="Enviar mensagem (Ctrl+Enter)", 
                    background="#ffffe0", relief="solid", borderwidth=1)
    label.pack()
    tooltip.after(3000, tooltip.destroy)

btn_send.bind("<Enter>", show_tooltip)

def ctrl_enter_send(event):
    send_message()
root.bind('<Control-Return>', ctrl_enter_send)

try:
    prompt = sock.recv(1024).decode()
    nickname = simpledialog.askstring("Nickname", prompt, parent=root)
    if not nickname:
        nickname = "Anon"
    sock.send(nickname.encode())
except Exception as e:
    print(f"Erro na inicialização: {e}")
    nickname = "Anon"

t = threading.Thread(target=receive_messages, daemon=True)
t.start()

entry_msg.bind("<Return>", send_message)
entry_msg.focus()

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

add_system_message(f"[Sistema] Bem-vindo(a), {nickname}! Você se conectou ao chat.")

root.mainloop()
