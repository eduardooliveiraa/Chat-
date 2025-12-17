# 📊 Modelo de Dados - Chat E2E

## 1. Estruturas de Dados

### 1.1 User (Usuário)
```python
{
    "user_id": "ac4f8780a475",           # UUID único por sessão
    "username": "João",                   # Nome do usuário (1-20 caracteres)
    "socket_id": "kuawUugC9BID1B5RAAAC", # Socket.IO connection ID
    "joined_at": 1764565800,              # Timestamp de entrada
    "is_online": true                     # Status conectado/desconectado
}
```

### 1.2 Message (Mensagem)
```python
{
    "id": "msg_12345",                           # Identificador único
    "sender_id": "ac4f8780a475",                 # ID de quem enviou
    "sender_name": "João",                       # Nome do remetente
    "encrypted_content": "gAAAAABm7k9z8x5h...", # Conteúdo criptografado
    "timestamp": 1764565801,                     # Quando foi enviada
    "type": "public" | "private",                # Tipo de mensagem
    "recipient_id": "c9b23551acbd"               # Para mensagens privadas
}
```

### 1.3 Reaction (Reação)
```python
{
    "message_id": "msg_12345",        # Mensagem que foi reagida
    "emoji": "❤️",                    # Emoji da reação
    "user_id": "ac4f8780a475",        # Quem reagiu
    "timestamp": 1764565802           # Quando foi reagido
}
```

### 1.4 Encryption Data (Dados de Criptografia)
```python
{
    "password": "minha_senha_segura",        # Senha da sala (não armazenada)
    "salt": "base64_encoded_random_bytes",   # Salt derivado de PBKDF2
    "key": "256_bit_key_derived",            # Chave derivada (no cliente)
    "iv": "random_16_bytes_per_message",     # Initialization Vector (aleatório)
    "algorithm": "AES-256-GCM"               # Algoritmo de criptografia
}
```

## 2. Armazenamento em Memória

### No Servidor (app.py)

```python
# Usuários conectados
users = {
    "ac4f8780a475": {
        "socket_id": "kuawUugC9BID1B5RAAAC",
        "username": "João",
        "joined_at": 1764565800
    },
    # ... mais usuários
}

# Histórico de mensagens públicas (últimas 100)
messages = [
    {
        "sender_id": "ac4f8780a475",
        "sender_name": "João",
        "encrypted_content": "gAAAAABm7k9z8x5h...",
        "timestamp": 1764565801,
        "type": "public"
    },
    # ... até 100 mensagens
]

# Mensagens privadas por conversa (Dict[conversa_id] = [messages])
private_messages = {
    "ac4f8780a475_c9b23551acbd": [
        {
            "sender_id": "ac4f8780a475",
            "encrypted_content": "gAAAAABm7k9z8x5h...",
            "timestamp": 1764565801,
            "type": "private"
        }
    ]
}

# Reações nas mensagens (Dict[message_id] = [reactions])
reactions = {
    "msg_12345": [
        {"emoji": "❤️", "user_id": "ac4f8780a475"},
        {"emoji": "😂", "user_id": "c9b23551acbd"}
    ]
}
```

### No Cliente (templates/chat.html)

```javascript
// Dados do usuário conectado
{
    username: "João",
    userId: "ac4f8780a475",
    encryptionPassword: "minha_senha_segura" // Nunca enviado ao servidor
}

// Mensagens locais em cache
messages = [
    {
        sender: "João",
        content: "Olá!", // Descriptografado no cliente
        timestamp: 1764565801,
        encrypted: "gAAAAABm7k9z8x5h...",
        isOwn: true
    }
];

// Chave de criptografia derivada
cryptoKey = CryptoKey; // Web Crypto API object
```

## 3. Fluxo de Dados

### Enviar Mensagem

```
Cliente:
  1. Usuário digita: "Olá!"
  2. Gera IV aleatório: [16 bytes aleatórios]
  3. Criptografa com AES-256-GCM: {iv: "...", ciphertext: "..."}
  4. Envia socket.emit('message', {encrypted_content: "..."})
         ↓
Servidor:
  5. Recebe sem descriptografar
  6. Armazena em memória
  7. Broadcast para todos: socket.emit('message', data)
         ↓
Outros Clientes:
  8. Recebem mensagem criptografada
  9. Descriptografam com mesma senha
  10. Exibem "Olá!" descriptografado
```

### Conversa Privada

```
Cliente A:
  1. Clica em "João"
  2. Envia socket.emit('private_message', {recipient_id, encrypted_content})
         ↓
Servidor:
  3. Armazena em private_messages[sender_id_recipient_id]
  4. Envia apenas para Cliente B via direct emit
         ↓
Cliente B:
  5. Recebe notificação
  6. Descriptografa
  7. Exibe conversa privada
```

## 4. Restrições de Dados

| Campo | Tipo | Min | Max | Validação |
|-------|------|-----|-----|-----------|
| username | string | 1 | 20 | Alfanumérico + espaços |
| password | string | 4 | 50 | Qualquer caractere |
| message | string | 1 | 5000 | Qualquer caractere |
| emoji | string | 1 | 2 | Unicode emoji |
| messages_history | array | 0 | 100 | Circular buffer |
| reactions_per_msg | array | 0 | ∞ | Sem limite |
| max_connections | int | - | 50+ | Teórico |

## 5. Persistência

**Nada é persistido entre reinicializações do servidor!**

- ❌ Não salva em banco de dados
- ❌ Não salva em arquivo
- ✅ Tudo em RAM (rápido mas volátil)
- ✅ Histórico se perde ao reiniciar

**Por design**: Mensagens desaparecem = privacidade garantida
