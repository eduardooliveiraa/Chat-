from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
from cryptography.fernet import Fernet
import base64
import hashlib
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

users = {}
user_ids = {}
chat_history = []
private_messages = {}
message_reactions = {}
MAX_HISTORY = 100

def setup_encryption():
    key_file = 'server.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
        print("Chave de criptografia carregada")
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        print("Nova chave de criptografia gerada")
    return Fernet(key)

cipher = setup_encryption()

def encrypt_message(message):
    try:
        return cipher.encrypt(message.encode()).decode()
    except:
        return None

def decrypt_message(encrypted_message):
    try:
        return cipher.decrypt(encrypted_message.encode()).decode()
    except:
        return None

def generate_user_id(username):
    return hashlib.sha256(f"{username}_{uuid.uuid4()}".encode()).hexdigest()[:12]

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    print(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in users:
        user_data = users[sid]
        username = user_data['username']
        user_id = user_data['user_id']
        
        del users[sid]
        if user_id in user_ids:
            del user_ids[user_id]
        
        timestamp = datetime.now().strftime('%H:%M')
        emit('user_left', {
            'username': username,
            'timestamp': timestamp,
            'online_count': len(users)
        }, broadcast=True)
        
        broadcast_online_users()
        print(f"{username} desconectou")

def broadcast_online_users():
    user_list = [{'user_id': u['user_id'], 'username': u['username']} for u in users.values()]
    emit('online_users', {
        'users': user_list,
        'count': len(users)
    }, broadcast=True)

@socketio.on('join')
def handle_join(data):
    username = data.get('username', 'Anonimo').strip()
    if not username:
        username = 'Anonimo'
    
    if len(username) > 20:
        username = username[:20]
    
    user_id = generate_user_id(username)
    
    users[request.sid] = {
        'username': username,
        'user_id': user_id,
        'sid': request.sid
    }
    user_ids[user_id] = request.sid
    
    timestamp = datetime.now().strftime('%H:%M')
    
    emit('joined', {'user_id': user_id, 'username': username})
    
    for msg in chat_history[-50:]:
        msg_copy = msg.copy()
        if msg['id'] in message_reactions:
            msg_copy['reactions'] = message_reactions[msg['id']]
        emit('encrypted_message', msg_copy)
    
    emit('user_joined', {
        'username': username,
        'timestamp': timestamp,
        'online_count': len(users)
    }, broadcast=True)
    
    broadcast_online_users()
    print(f"{username} entrou no chat (ID: {user_id})")

@socketio.on('send_encrypted_message')
def handle_encrypted_message(data):
    sid = request.sid
    if sid not in users:
        return
    
    user_data = users[sid]
    username = user_data['username']
    user_id = user_data['user_id']
    encrypted_content = data.get('encrypted', '').strip()
    
    if not encrypted_content or len(encrypted_content) > 5000:
        return
    
    timestamp = datetime.now().strftime('%H:%M')
    msg_id = str(uuid.uuid4())[:8]
    
    msg_data = {
        'id': msg_id,
        'username': username,
        'user_id': user_id,
        'encrypted': encrypted_content,
        'timestamp': timestamp,
        'type': 'public',
        'reactions': {}
    }
    
    chat_history.append(msg_data)
    if len(chat_history) > MAX_HISTORY:
        chat_history.pop(0)
    
    message_reactions[msg_id] = {}
    
    emit('encrypted_message', msg_data, broadcast=True)

@socketio.on('send_private_encrypted')
def handle_private_encrypted(data):
    sid = request.sid
    if sid not in users:
        return
    
    sender_data = users[sid]
    sender_name = sender_data['username']
    sender_id = sender_data['user_id']
    target_user_id = data.get('target_user_id')
    encrypted_content = data.get('encrypted', '').strip()
    
    if not encrypted_content or len(encrypted_content) > 5000 or not target_user_id:
        return
    
    if target_user_id not in user_ids:
        emit('error', {'message': 'Usuario nao encontrado ou offline'})
        return
    
    target_sid = user_ids[target_user_id]
    if target_sid not in users:
        emit('error', {'message': 'Usuario nao encontrado'})
        return
    
    recipient_data = users[target_sid]
    recipient_name = recipient_data['username']
    
    timestamp = datetime.now().strftime('%H:%M')
    msg_id = str(uuid.uuid4())[:8]
    
    msg_data = {
        'id': msg_id,
        'sender': sender_name,
        'sender_id': sender_id,
        'recipient': recipient_name,
        'recipient_id': target_user_id,
        'encrypted': encrypted_content,
        'timestamp': timestamp,
        'type': 'private'
    }
    
    chat_key = tuple(sorted([sender_id, target_user_id]))
    if chat_key not in private_messages:
        private_messages[chat_key] = []
    private_messages[chat_key].append(msg_data)
    
    if len(private_messages[chat_key]) > 100:
        private_messages[chat_key] = private_messages[chat_key][-100:]
    
    emit('private_encrypted', msg_data, room=sid)
    if target_sid != sid:
        emit('private_encrypted', msg_data, room=target_sid)

@socketio.on('get_private_history')
def handle_get_private_history(data):
    sid = request.sid
    if sid not in users:
        return
    
    my_user_id = users[sid]['user_id']
    target_user_id = data.get('target_user_id')
    
    if not target_user_id:
        return
    
    chat_key = tuple(sorted([my_user_id, target_user_id]))
    history = private_messages.get(chat_key, [])
    
    emit('private_history', {'messages': history[-50:], 'target_user_id': target_user_id})

@socketio.on('add_reaction')
def handle_reaction(data):
    sid = request.sid
    if sid not in users:
        return
    
    msg_id = data.get('msg_id')
    emoji = data.get('emoji')
    username = users[sid]['username']
    
    if not msg_id or not emoji:
        return
    
    is_public_msg = any(m['id'] == msg_id for m in chat_history)
    if not is_public_msg:
        return
    
    if msg_id not in message_reactions:
        message_reactions[msg_id] = {}
    
    if emoji not in message_reactions[msg_id]:
        message_reactions[msg_id][emoji] = []
    
    if username in message_reactions[msg_id][emoji]:
        message_reactions[msg_id][emoji].remove(username)
        if not message_reactions[msg_id][emoji]:
            del message_reactions[msg_id][emoji]
    else:
        message_reactions[msg_id][emoji].append(username)
    
    emit('reaction_updated', {
        'msg_id': msg_id,
        'reactions': message_reactions[msg_id]
    }, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    sid = request.sid
    if sid not in users:
        return
    
    user_data = users[sid]
    target_user_id = data.get('target_user_id')
    
    typing_data = {
        'username': user_data['username'],
        'user_id': user_data['user_id'],
        'is_typing': data.get('is_typing', False)
    }
    
    if target_user_id and target_user_id in user_ids:
        target_sid = user_ids[target_user_id]
        typing_data['is_private'] = True
        emit('user_typing', typing_data, room=target_sid)
    else:
        emit('user_typing', typing_data, broadcast=True, include_self=False)

@socketio.on('get_online_users')
def handle_get_online_users():
    user_list = [{'user_id': u['user_id'], 'username': u['username']} for u in users.values()]
    emit('online_users', {
        'users': user_list,
        'count': len(users)
    })

if __name__ == '__main__':
    print("=== SERVIDOR DE CHAT SEGURO ===")
    print("Iniciando em http://0.0.0.0:5000")
    print("Mensagens sao criptografadas no cliente")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
