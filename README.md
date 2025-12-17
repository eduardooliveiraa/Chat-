# 💬 Chat - Aplicação com Criptografia

Um aplicativo de chat em tempo real com criptografia e mensagens privadas

## ✨ Características

✅ Criptografia E2E verdadeira (AES-256-GCM)  
✅ Mensagens privadas 1v1  
✅ Chat em tempo real (WebSocket)  
✅ Interface responsiva  
✅ Sem registro necessário  

## 🔐 Como Funciona

A criptografia é baseada em **senha da sala**:

1. Você digita um nome e uma senha
2. A senha é usada para derivar uma chave (PBKDF2 com 100k iterações)
3. Todas as mensagens são criptografadas no seu navegador com AES-256-GCM
4. O servidor recebe apenas texto criptografado e **não vê o conteúdo**
5. Outros usuários com a mesma senha conseguem descriptografar

**Todos precisam usar a mesma senha para ler as mensagens!**

## 🚀 Como Usar

### Entrar no Chat

```
1. Nome: Digite seu nome (até 20 caracteres)
2. Senha: Digite a senha da sala (compartilhe com amigos por outro meio)
3. Clique: "Entrar no Chat"
```

### Funcionalidades

| Função | Como fazer |
|--------|-----------|
| **Chat Geral** | Mensagens aparecem para todos |
| **Mensagens Privadas** | Clique em um usuário na barra lateral |
| **Emojis** | Clique no botão 😀 antes de enviar |
| **Reações** | Passe mouse + clique "+" em uma mensagem |
| **Indicador** | Aparece quando alguém está digitando |

## 🌐 Testar em Múltiplas Máquinas

### Opção 1: URL de Desenvolvimento
1. Copie a URL da visualização
2. Abra em outro navegador/celular/máquina
3. Use mesmo nome + **mesma senha**

## 🛠️ Tecnologia

| Parte | Stack |
|------|-------|
| **Backend** | Flask + Flask-SocketIO + Eventlet |
| **Frontend** | HTML/CSS/JavaScript Vanilla |
| **Criptografia** | PBKDF2 + AES-256-GCM (Web Crypto API) |
| **Comunicação** | WebSocket (Socket.IO) |
| **Armazenamento** | Em memória (100 mensagens) |

## 📋 Limitações

- Mensagens perdidas ao reiniciar servidor
- Sem persistência em banco de dados
- Sem autenticação
- Máximo ~50 usuários simultâneos

## 📖 Documentação

- **VISION.md** - Visão do produto e objetivos
- **DATA_MODEL.md** - Estrutura de dados
- **ARCHITECTURE.md** - Diagrama de componentes e fluxo

## 🧪 Testar Criptografia Real

1. Abra DevTools (F12)
2. Vá para Network/Rede
3. Envie uma mensagem
4. Procure requisição Socket.IO
5. Veja que o conteúdo é criptografado (só bytes aleatórios)