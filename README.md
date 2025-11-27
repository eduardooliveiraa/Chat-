# 💬 Chat distribuído com Python e Tkinter

## 📘 Descrição

Este projeto consiste em um chat distribuído simples, composto por:

1. Servidor TCP multicliente:

- Implementado em Python usando socket e threading.

- Escuta conexões em uma porta definida (PORT = 5000).

- Cada cliente conectado recebe mensagens de todos os outros em tempo real.

- Mensagens do sistema indicam quando usuários entram no chat.

2. Cliente com interface Tkinter:

- Conecta ao servidor e permite envio/recepção de mensagens.

- Interface gráfica estilizada.

O sistema permite múltiplos clientes conectados simultaneamente, funcionando de forma distribuída.

## ⚙️ Como funciona

1. O servidor roda em uma máquina que aceita conexões TCP.

2. Os clientes se conectam ao IP da máquina servidor e porta configurada.

3. Cada cliente escolhe um nickname ao entrar.

4. O servidor repassa todas as mensagens recebidas a todos os clientes conectados, exceto o remetente.

5. O cliente exibe mensagens recebidas em uma GUI, separando mensagens de sistema das mensagens normais.

Comandos especiais:

/sair → desconecta o cliente do servidor e fecha a interface.

## 📦 Pré-requisitos

- Python 3 (3.8+ recomendado).  
- Módulos padrão: `socket`, `threading`, `tkinter`, `datetime`, `re`.  
- Rede local ou VPN para conexão entre máquinas.  

## 🚀 Como Executar

### 🖥️ Servidor

1. Ajuste IP e porta se necessário (opcional):

```python
HOST = "0.0.0.0"  # Aceita conexões de qualquer interface
PORT = 5000       # Porta do servidor
```
2. Execute o servidor:
```bash
python3 server.py
```
### 💻 Cliente

1. Ajuste o IP do servidor no arquivo do cliente (client.py):

```python
HOST = "IP_DO_SERVIDOR"  # Ex: "192.168.0.100"
PORT = 5000
```
2. Execute o cliente:
```bash
python3 client.py
```
3. Digite seu nickname quando solicitado.

4. A interface do chat será exibida automaticamente.

## ⌨️ Comandos do Cliente

/sair → desconectar do chat.

Enter → enviar mensagem.

## 📝 Observações Importantes

- O servidor deve estar rodando antes de qualquer cliente se conectar.

- Todos os clientes devem usar o mesmo IP e porta do servidor.

- Caso a conexão seja perdida, a interface exibirá status Desconectado.