# 🏗️ Diagrama de Componentes - Chat E2E

## 1. Arquitetura de Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET / REDE                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐         ┌───▼────┐        ┌───▼────┐
    │ Cliente │         │ Cliente │        │ Cliente │
    │  Web A  │         │  Web B  │        │  Celular│
    │(Chrome) │         │(Firefox)│        │ (Mobile)│
    └────┬────┘         └────┬────┘        └────┬────┘
         │                   │                   │
         │  WebSocket        │  WebSocket        │  WebSocket
         │  Socket.IO        │  Socket.IO        │  Socket.IO
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  SERVIDOR FLASK │
                    │  +Socket.IO     │
                    │  (port 5000)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │ Usuários │         │Histórico│        │ Reações │
    │  (RAM)   │         │(RAM)    │        │ (RAM)   │
    │ Max 50   │         │100 msgs │        │ Dict    │
    └──────────┘         └─────────┘        └─────────┘
```

## 2. Arquitetura Cliente (Frontend)

```
┌──────────────────────────────────────────────────┐
│              NAVEGADOR DO CLIENTE                │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────┐   │
│  │     templates/chat.html (UI)            │   │
│  ├────────────────────────────────────────┤   │
│  │  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ Login Screen │  │ Chat Window  │   │   │
│  │  ├──────────────┤  ├──────────────┤   │   │
│  │  │ - Username   │  │ - Mensagens  │   │   │
│  │  │ - Password   │  │ - Usuários   │   │   │
│  │  │ - Enter btn  │  │ - Input msg  │   │   │
│  │  └──────────────┘  │ - Emojis     │   │   │
│  │                    └──────────────┘   │   │
│  └────────────────────────────────────────┘   │
│                         ▲                      │
│         ┌───────────────┼───────────────┐    │
│         │               │               │    │
│  ┌──────▼───────┐ ┌─────▼──────┐ ┌────▼────┐│
│  │  Socket.IO   │ │ Encryption │ │DOM Utils││
│  │  Client      │ │ (PBKDF2 +  │ │ (Query,│
│  │              │ │ AES-256-GCM)│ │ Update)││
│  │ - connect()  │ │            │ │        ││
│  │ - emit()     │ │ - derive() │ │ - text ││
│  │ - on()       │ │ - encrypt()│ │ - HTML ││
│  │ - disconnect │ │ - decrypt()│ │ - style││
│  └──────────────┘ └────────────┘ └────────┘│
│                                            │
│  ┌──────────────────────────────────┐     │
│  │ LocalStorage/SessionStorage      │     │
│  │ - username                       │     │
│  │ - messages cache                 │     │
│  │ - active_conversation_id         │     │
│  └──────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

## 3. Arquitetura Servidor (Backend)

```
┌──────────────────────────────────────────────────────┐
│              SERVIDOR PYTHON (app.py)                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────┐        │
│  │ Flask Application + Flask-SocketIO      │        │
│  ├─────────────────────────────────────────┤        │
│  │  ┌──────────┐  ┌──────────┐             │        │
│  │  │ HTTP     │  │ WebSocket│             │        │
│  │  │ Routes   │  │ Events   │             │        │
│  │  ├──────────┤  ├──────────┤             │        │
│  │  │ GET /    │  │ 'join'   │             │        │
│  │  │ (HTML)   │  │ 'message'│             │        │
│  │  │          │  │ 'typing' │             │        │
│  │  │          │  │ 'reaction│             │        │
│  │  │          │  │ 'private'│             │        │
│  │  │          │  │ 'leave'  │             │        │
│  │  └──────────┘  └──────────┘             │        │
│  └─────────────────────────────────────────┘        │
│           ▲                                          │
│  ┌────────┴────────────────────┐                    │
│  │                             │                    │
│ ┌▼──────────────┐  ┌──────────▼──┐                 │
│ │ Data Manager  │  │ Event Handler│                │
│ ├───────────────┤  ├──────────────┤                │
│ │               │  │              │                │
│ │ users dict    │  │ @socketio.on │                │
│ │ messages list │  │ decorators   │                │
│ │ private_msgs  │  │              │                │
│ │ reactions dict│  │ - Broadcast  │                │
│ │               │  │ - Send to one│                │
│ │ Thread Lock   │  │ - Update list│                │
│ │ (Sync)        │  │              │                │
│ └───────────────┘  └──────────────┘                │
│                                                     │
│  ┌──────────────────────────────────┐              │
│  │ Encryption Engine                │              │
│  │ (Cryptography Library)           │              │
│  │                                  │              │
│  │ - NEVER decrypts messages        │              │
│  │ - NEVER stores plaintext         │              │
│  │ - Stores only ciphertext         │              │
│  └──────────────────────────────────┘              │
└──────────────────────────────────────────────────────┘
```

## 4. Fluxo de Dados (Message Flow)

### Publicar Mensagem

```
┌─────────────┐
│   Cliente   │ Digita "Olá!" + Enter
└────────────┬┘
             │
             ▼
    ┌────────────────────┐
    │ Gera IV aleatório  │
    │ Criptografa        │
    │ AES-256-GCM        │
    └────────┬───────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ socket.emit('message', {         │
    │   encrypted_content: "gAAA..."   │
    │ })                               │
    └────────┬─────────────────────────┘
             │
          WEB│SOCKET
             ▼
    ┌─────────────────────────────┐
    │ Servidor (app.py)           │
    │ - Recebe                    │
    │ - NÃO descriptografa        │
    │ - Armazena como está        │
    │ - Broadcast p/ todos        │
    └────┬────────────────┬───────┘
         │                │
      WEB│SOCKET       WEB│SOCKET
         │                │
         ▼                ▼
    ┌─────────┐      ┌─────────┐
    │Cliente B│      │Cliente C│
    │Recebe   │      │Recebe   │
    │cripto   │      │cripto   │
    │Decripto │      │Decripto │
    │Exibe    │      │Exibe    │
    │"Olá!"   │      │"Olá!"   │
    └─────────┘      └─────────┘
```

### Mensagem Privada

```
┌────────────┐              ┌────────────┐
│  Cliente A │              │  Cliente B │
│ (João)     │              │ (Maria)    │
└─────┬──────┘              └─────┬──────┘
      │                           │
      │ Clica em Maria            │
      │ Digita mensagem           │
      │ Criptografa               │
      │ Envia socket.emit()       │
      │                           │
      └──────────────────────────►│
                                  │
                 ┌────────────────►│
                 │ Servidor       │
                 │ - Recebe       │
                 │ - Armazena em  │
                 │   private_msgs │
                 │ - Emite direto │
                 │   para Cliente B
                 │                │
                 │        PRIVADO │
                 │        SÓ B    │
                 │                │
                 └────────────────►│
                                  │
                              Decripto
                              Exibe
```

## 5. Fluxo de Segurança (Criptografia)

```
Usuário digita senha
         ▼
┌─────────────────────────────┐
│ PBKDF2-SHA256               │
│ - Entrada: Senha            │
│ - Iterações: 100.000        │
│ - Output: 256-bit Key       │
└──────────┬──────────────────┘
           ▼
      Chave Derivada
           ▼
┌──────────────────────────────────┐
│ Para cada mensagem:              │
│ 1. Gera IV (16 bytes aleatório) │
│ 2. AES-256-GCM Encrypt         │
│ 3. Output: IV + Ciphertext     │
│ 4. JSON encode + envia         │
└──────────┬───────────────────────┘
           ▼
      Servidor recebe
      Sem poder abrir
           ▼
      Broadcast para outros
           ▼
      Outros clientes:
      1. Recebem IV + Ciphertext
      2. Derivam mesma chave (mesma senha)
      3. AES-256-GCM Decrypt
      4. Veem plaintext
```

## 6. Componentes Principais

| Componente | Localização | Responsabilidade |
|-----------|-------------|-----------------|
| **app.py** | Backend | Servidor Flask, gerencia WebSocket |
| **chat.html** | Frontend | UI, criptografia, Socket.IO client |
| **PBKDF2** | Frontend (Web Crypto) | Derivar chave da senha |
| **AES-256-GCM** | Frontend (Web Crypto) | Criptografar/descriptografar |
| **Socket.IO** | Frontend + Backend | Comunicação real-time |
| **Eventlet** | Backend | Async networking |
| **CORS** | Backend | Permitir requisições cross-origin |

## 7. Matriz de Comunicação

```
                Servidor          Cliente A          Cliente B
┌─────────────┬─────────────┬─────────────┬──────────────┐
│ Tipo        │ Qual evento │ O que envia │ O que recebe │
├─────────────┼─────────────┼─────────────┼──────────────┤
│ Join        │ 'join'      │ {username}  │ user_joined  │
│ Message     │ 'message'   │ {ciphertext}│ message      │
│ Typing      │ 'typing'    │ {username}  │ user_typing  │
│ Private msg │ 'priv_msg'  │ {recipient, │ private_msg  │
│             │             │  ciphertext}│              │
│ Reaction    │ 'reaction'  │ {msg_id,    │ reaction_add │
│             │             │  emoji}     │              │
│ Leave       │ 'leave'     │ {username}  │ user_left    │
│ Typing stop │ (timeout)   │ N/A         │ typing_stop  │
└─────────────┴─────────────┴─────────────┴──────────────┘
```
