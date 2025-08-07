# Wiki Chatbot - Assistente Inteligente para Operadoras

## 📋 Descrição

Chatbot inteligente desenvolvido para consultar informações de operadoras através da API GraphQL do Wiki.js. O sistema oferece uma interface moderna e responsiva com widget flutuante para fácil integração em qualquer página.

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** - Token seguro para acesso à API
- 📊 **Consultas GraphQL** - Integração direta com Wiki.js
- 🎯 **Busca Inteligente** - Divisão de conteúdo por tags H2
- 🧹 **Limpeza HTML** - Processamento otimizado de conteúdo
- 📱 **Interface Responsiva** - Design moderno e adaptável
- 🎨 **Widget Flutuante** - Ícone no canto da tela para integração
- ⚡ **Tempo Real** - Respostas instantâneas via API

## 🚀 Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: GraphQL (Wiki.js)
- **Autenticação**: JWT Token
- **Estilo**: Gradientes modernos, animações CSS
- **Ícones**: Font Awesome

## 📁 Estrutura do Projeto

```
operadoras/
├── wiki_chatbot.py              # Servidor Flask principal
├── config.py                    # Configurações e JWT token
├── teste_wiki_chatbot.py        # Script de testes
├── requirements.txt             # Dependências Python
├── templates/
│   ├── wiki_chatbot.html        # Interface completa
│   └── chatbot_widget.html      # Widget flutuante
└── README_WIKI_CHATBOT.md       # Documentação detalhada
```

## ⚙️ Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/FADUL37/Wiki-Chatbot.git
cd Wiki-Chatbot
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o JWT Token
Edite o arquivo `config.py` e adicione seu token JWT válido:
```python
JWT_TOKEN = "seu_token_jwt_aqui"
```

### 4. Execute o servidor
```bash
python wiki_chatbot.py
```

## 🌐 Endpoints Disponíveis

- **`/`** - Interface completa do chatbot
- **`/widget`** - Widget flutuante (apenas ícone)
- **`/chat`** - API para envio de mensagens (POST)
- **`/operadoras`** - Lista todas as operadoras disponíveis
- **`/consulta/<operadora>/<topico>`** - Consulta específica
- **`/teste_api`** - Teste de conectividade da API

## 💬 Como Usar

### Interface Completa
1. Acesse `http://localhost:5000`
2. Digite sua pergunta no campo de texto
3. Receba respostas em tempo real

### Widget Flutuante
1. Acesse `http://localhost:5000/widget`
2. Clique no ícone flutuante no canto direito
3. Interaja com o chatbot

### Integração em Outras Páginas
```html
<!-- Opção 1: iframe -->
<iframe src="http://localhost:5000/widget" width="100%" height="100%"></iframe>

<!-- Opção 2: Copiar código do chatbot_widget.html -->
```

## 🎨 Características do Design

- **Gradientes Modernos**: Cores vibrantes e profissionais
- **Animações Suaves**: Transições fluidas e elegantes
- **Responsivo**: Adaptável a desktop e mobile
- **Acessível**: Interface intuitiva e amigável
- **Partículas Animadas**: Fundo dinâmico e atrativo

## 🔧 Personalização

### Alterar Cores
Edite as variáveis CSS em `chatbot_widget.html`:
```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cores personalizadas */
--primary-color: #667eea;
--secondary-color: #764ba2;
```

### Modificar Sugestões
Edite as sugestões no arquivo HTML:
```html
<div class="suggestion-chip" onclick="sendSuggestion('Sua pergunta')">
    Sua Sugestão
</div>
```

## 🚀 Deploy para Produção

### Render.com
1. Faça push para GitHub
2. Conecte o repositório no Render
3. Configure as variáveis de ambiente
4. Deploy automático

### Configurações de Produção
```python
# Modificar wiki_chatbot.py para produção
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

## 📊 Funcionalidades da API

- ✅ **41 Operadoras Configuradas**
- ✅ **Consulta GraphQL em Tempo Real**
- ✅ **Divisão de Conteúdo por H2**
- ✅ **Busca Inteligente de Tópicos**
- ✅ **Limpeza Avançada de HTML**
- ✅ **Respostas Estruturadas**
- ✅ **Tratamento de Erros**

## 🧪 Testes

Execute o script de testes:
```bash
python teste_wiki_chatbot.py
```

## 📝 Exemplos de Uso

```python
# Consulta via API
import requests

response = requests.post('http://localhost:5000/chat', 
    json={'pergunta': 'Qual o telefone da VIVAS?'})
print(response.json())
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para consultas inteligentes de operadoras.

## 🔗 Links Úteis

- [Documentação Wiki.js](https://docs.requarks.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GraphQL](https://graphql.org/)

---

**Status**: ✅ Totalmente Funcional | **Versão**: 1.0.0 | **Última Atualização**: Janeiro 2025