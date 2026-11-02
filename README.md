# 🎸 Empório da Música — Agente de Atendimento Inteligente para WhatsApp

Assistente conversacional inteligente em Python desenvolvido para atender clientes da loja **Empório da Música** (Campo Grande/MS) via WhatsApp e linha de comando.

---

## 🧭 Fluxo de Navegação do Usuário e Regras de Atendimento

O agente **"Afinado"** foi projetado seguindo as melhores práticas de experiência conversacional (UX conversacional):

### 1. Saudação Inicial e Apresentação dos Grandes Temas
Na primeira interação, o assistente acolhe o cliente e apresenta os **4 tópicos principais** mais procurados, permitindo que o cliente escolha um número ou digite com suas próprias palavras:
- 🎸 **1. Preço e Disponibilidade de Produtos** (consulta de instrumentos em estoque, marcas, ficha técnica e desconto no PIX de 5%)
- 📦 **2. Status e Rastreamento de Pedido** (acompanhamento de entregas por código ou número do pedido)
- ⏰ **3. Horários de Funcionamento e Loja Física** (endereço no centro de Campo Grande/MS e expediente)
- 💳 **4. Políticas de Pagamento, Frete e Devolução** (parcelamento sem juros, frete com motoboy próprio e devolução pelo CDC em até 7 dias)

### 2. Resolução do Problema + Pergunta de Acompanhamento (Follow-Up)
Quando o cliente envia uma dúvida:
1. O agente resolve o problema imediatamente com dados precisos do catálogo ou das políticas.
2. Em seguida, adiciona uma **pergunta de acompanhamento contextual** relacionada aos grandes tópicos para dar continuidade natural ao atendimento (ex.: após consultar o preço de um violão, pergunta se deseja simular parcelamento ou calcular o frete).

### 3. Tempo de Resposta (SLA Máximo de 5 Minutos)
- Respostas geradas com agilidade, cumprindo a diretriz operacional da empresa de tempo máximo de resposta de até 5 minutos durante o expediente comercial (Segunda a Sexta 09h às 18h e Sábados 09h às 13h).

### 4. Transbordo Humano Proativo (Limite de 4 Perguntas)
- O sistema mantém a contagem de turnos da conversa.
- Se o cliente já fez **4 ou mais perguntas**, o agente verifica com empatia se ele está conseguindo encontrar as respostas que procura e oferece proativamente a opção de falar diretamente com um atendente humano pelo WhatsApp **(67) 3321-4500** ou telefone **(67) 3341-4444**.

### 5. Guardrails e Restrições de Escopo
- **Exclusividade de Instrumentos**: A loja comercializa exclusivamente instrumentos musicais. Pedidos de acessórios (cordas, palhetas, cabos, cases, pedais ou amplificadores) são educadamente recusados e redirecionados para parceiros.
- **Assuntos Fora da Loja**: Perguntas aleatórias (receitas, política, programação, etc.) são gentilmente recusadas com redirecionamento de foco.
- **Promoções Expiradas**: Transparência total para promoções inativas no sistema (ex: Takamine GD20 com 12% off encerrado), informando o valor de tabela atual sem alucinar descontos passados.

---

## 🏗️ Estrutura do Projeto

```
emporio_da_musica_agent/
├── app/
│   ├── agent/
│   │   ├── brain.py          # Gerenciador de histórico, contador de turnos e ReAct loop
│   │   ├── persona.py        # System prompt, tom acolhedor, SLA e diretrizes de navegação
│   │   └── tools.py          # Function calling (produtos, pedidos, políticas, transbordo)
│   ├── api/
│   │   └── webhook.py        # Webhook FastAPI para o Meta WhatsApp Cloud API
│   ├── database/
│   │   └── db.py             # SQLite em memória alimentado pelos CSVs da empresa
│   ├── knowledge/
│   │   ├── catalog.py        # Catálogo com filtros de estoque, preço e promoções
│   │   ├── orders.py         # Rastreamento de pedidos e junção de dados de clientes
│   │   └── policies.py       # Leitor e sintetizador das políticas da empresa
│   ├── services/
│   │   └── whatsapp.py       # Envio de mensagens via Meta Graph API v20.0
│   ├── config.py             # Configurações de ambiente (OpenAI, Gemini, Ollama)
│   └── main.py               # Servidor FastAPI com rotas de saúde e webhook
├── data/
│   ├── desafio_tecnico_ai_eng - *.csv  # Tabelas originais da empresa
│   ├── politicas_da_loja.json          # Políticas estruturadas
│   └── políticas_da_loja.pdf           # Manual oficial de atendimento
├── cli_test.py               # Simulador interativo via terminal
├── requirements.txt          # Dependências
├── .env.example              # Modelo de variáveis de ambiente
├── .gitignore
└── README.md
```

---

## 🚀 Como Executar

### 1. Criar e Ativar Ambiente Virtual
```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux / Mac:
source venv/bin/activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example`:
```bash
cp .env.example .env
```
Abra o `.env` e configure sua chave de API para o provedor de LLM desejado (OpenAI, Google Gemini, Groq ou Ollama).

---

## 🧪 Testando o Agente no Terminal

Para iniciar o simulador interativo:
```bash
python cli_test.py
```

### Exemplos para testar a navegação:
1. **Saudação inicial:** Digite `"Olá!"` para receber o menu com os 4 grandes tópicos.
2. **Consulta com follow-up:** Digite `"Quais violões custando até 1000?"` para receber os modelos em estoque e a pergunta de acompanhamento sobre frete ou parcelamento.
3. **Limite de 4 perguntas:** Continue interagindo e observe a oferta proativa de atendimento humano a partir da 4ª pergunta.
4. **Restrição de escopo:** Pergunte `"Vocês vendem encordoamento ou palhetas?"` para verificar o guardrail de não venda de acessórios.
5. **Horários e SLA:** Pergunte `"Qual o horário de funcionamento?"` para verificar as informações de atendimento e o compromisso de resposta em até 5 minutos.

---

## 🌐 Rodando o Servidor Webhook do WhatsApp

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Acesse a documentação Swagger em: `http://localhost:8000/docs`
