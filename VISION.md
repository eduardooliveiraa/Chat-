# 📋 Documento de Visão - Chat com Criptografia E2E

## Visão do Produto

Aplicativo de chat web em tempo real com criptografia, permitindo comunicação segura entre usuários.

## Objetivos Principais

1. **Segurança**: Criptografia AES-256-GCM no cliente, servidor vê apenas texto criptografado
2. **Simplicidade**: Sem autenticação ou registro - apenas nome + senha da sala
3. **Tempo Real**: Comunicação instantânea via WebSocket (Socket.IO)
4. **Usabilidade**: Interface moderna, responsiva, funciona em desktop e celular
5. **Funcionalidades**: Chat geral, mensagens privadas, reações com emojis

## Características Principais

✅ Chat público em tempo real  
✅ Mensagens privadas 1v1  
✅ Lista de usuários online  
✅ Criptografia client-side  
✅ Interface responsiva  
✅ Sem registro necessário  

## Modelo de Segurança

```
Entrada: [Senha da Sala] + [PBKDF2 (100k iterações)]
         ↓
Chave de Criptografia: [256-bit AES Key]
         ↓
Cada Mensagem: [Random IV] + [AES-256-GCM Encrypt] + [IV + Ciphertext]
         ↓
Servidor: Recebe e transmite apenas ciphertext
         ↓
Outros Clientes: Descriptografam com mesma senha
```

## Restrições & Limitações

- Mensagens perdidas ao reiniciar servidor (em memória)
- Sem persistência de dados entre sessões
- Sem autenticação de usuários
- Sem banco de dados
- Máximo 100 mensagens por conversa

## Sucesso Medido Por

- ✅ Mensagens aparecem instantaneamente em todos os clientes
- ✅ Teste de segurança mostra criptografia real (DevTools Network)
- ✅ Funciona simultaneamente em múltiplos navegadores/dispositivos
- ✅ Interface responsiva em celular e desktop