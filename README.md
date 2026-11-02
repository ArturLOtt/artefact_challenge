# 🎸 Empório da Música - Agente de Atendimento WhatsApp

Agente inteligente em Python desenvolvido para atender clientes do **Empório da Música** via WhatsApp. Capaz de realizar consultoria de instrumentos, checagem de estoque e preços em tempo real, esclarecimento de dúvidas sobre políticas da empresa (trocas, garantias, frete, lutheria), rastreamento de pedidos e transbordo para atendimento humano, com guardrails estritos contra alucinações e desvios de assunto.

---

## 📂 Estrutura do Projeto

```
emporio_da_musica_agent/
├── app/
│   ├── agent/
│   │   ├── brain.py          # Orquestrador da conversa, memória de sessão e loop ReAct
│   │   ├── persona.py        # Prompt de sistema, tom de voz, regras de negócio e guardrails
│   │   └── tools.py          # Ferramentas dinâmicas (busca produtos, pedidos, políticas, transbordo)
│   ├── api/
│   │   └── webhook.py        # Webhook FastAPI para o Meta WhatsApp Cloud API (GET handshake + POST mensagens)
│   ├── knowledge/
│   │   ├── catalog.py        # Serviço de consulta e filtro de produtos e estoque
│   │   ├── orders.py         # Consulta de rastreamento e status de pedidos
│   │   └── policies.py       # Leitor e sintetizador das políticas da empresa
│   ├── services/
│   │   └── whatsapp.py       # Envio de mensagens e confirmação de leitura via Meta Graph API
│   ├── config.py             # Configurações com Pydantic Settings
│   └── main.py               # Servidor FastAPI e rotas de saúde
├── data/                     # Dados da empresa (substitua pelos seus dados reais)
│   ├── products.json         # Catálogo com instrumentos, acessórios, preços e estoque
│   ├── policies.json         # Políticas de troca, horários, endereço, frete e pagamento
│   └── orders.json           # Base de pedidos e códigos de rastreamento
├── cli_test.py               # Simulador interativo via terminal (não precisa de credenciais do WhatsApp)
├── requirements.txt          # Dependências do projeto
├── .env.example              # Modelo de variáveis de ambiente
└── README.md
```

---

## 🚀 Instalação Rápida

### 1. Criar e ativar o ambiente virtual (Recomendado)
```bash
python -m venv venv

# No Windows:
.\venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
Abra o `.env` e configure sua chave de API para o modelo de linguagem (LLM).

> 💡 **Flexibilidade de Provedor**: O agente suporta qualquer provedor compatível com a API OpenAI (incluindo OpenAI, **Google Gemini**, Groq e **Ollama** local):
> - **OpenAI**: `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_MODEL=gpt-4o-mini`
> - **Google Gemini**: `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`, `LLM_MODEL=gemini-2.5-flash`
> - **Ollama (Local/Gratuito)**: `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=llama3.1`

---

## 🧪 Testando o Agente no Terminal (Sem precisar do WhatsApp)

Você pode testar a inteligência, o tom de voz e as políticas do agente imediatamente através do simulador CLI:

```bash
python cli_test.py
```

### Exemplos de testes prontos:
1. **Recomendação de produto:**
   > *"Olá! Quais violões para iniciantes vocês têm e quanto custam?"*
2. **Políticas de pagamento:**
   > *"Tem desconto se eu pagar no PIX? Parcelam no cartão?"*
3. **Localização e horários:**
   > *"Qual o endereço da loja física e o horário de atendimento no sábado?"*
4. **Serviço de Lutheria:**
   > *"Vocês fazem regulagem de braço e troca de cordas?"*
5. **Rastreamento de pedido:**
   > *"Qual o status do meu pedido PED-1002?"*
6. **Guardrail (Fora de escopo):**
   > *"Qual a receita de um bolo de chocolate?"*
   *(O agente recusará educadamente e redirecionará para produtos da loja musical).*
7. **Transbordo humano:**
   > *"Quero falar com um atendente humano."*
   *(O agente acionará a ferramenta de suporte e fornecerá o contato direto).*

---

## 🌐 Rodando o Servidor do Webhook

Para iniciar o servidor FastAPI da aplicação:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse a documentação interativa da API no navegador:
`http://localhost:8000/docs`

---

## 📲 Conectando com o WhatsApp Cloud API (Meta)

1. Crie uma conta no [Meta for Developers](https://developers.facebook.com/) e adicione o produto **WhatsApp Business**.
2. Exponha sua porta local 8000 para a internet usando **ngrok** ou similar:
   ```bash
   ngrok http 8000
   ```
3. No painel da Meta:
   - Defina o **Callback URL** como: `https://seu-subdominio.ngrok-free.app/webhook`
   - Defina o **Verify Token** igual ao valor configurado em `WHATSAPP_VERIFY_TOKEN` no seu arquivo `.env`.
   - Assine o evento `messages`.
4. Adicione seu número de teste do WhatsApp no painel da Meta e envie uma mensagem para o número da empresa!

---

## 📝 Como Alimentar com os Dados Reais da sua Empresa

Quando você tiver os dados reais da sua loja:
1. **Produtos**: Edite o arquivo `data/products.json` com os produtos, especificações, preços e quantidades em estoque reais da sua empresa.
2. **Políticas**: Atualize o arquivo `data/policies.json` com os horários de funcionamento, regras de troca, endereços e condições de garantia oficiais.
3. **Pedidos**: Integre seu ERP/banco de dados ou substitua `data/orders.json` para consulta de status de entregas.
4. **Tom de Voz / Persona**: Ajuste as instruções no arquivo `app/agent/persona.py` para reforçar regras adicionais de atendimento.
