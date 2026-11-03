# 🎸 Empório da Música — Text message agent for WhatsApp

Intelligent conversational assistant in Python developed to serve customers of the **Empório da Música** store (Campo Grande/MS) via WhatsApp and command line

---

## 🚀 How to Run

### 1. Create and Activate a Virtual Environment
```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux / Mac:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the file `.env.example`:
```bash
cp .env.example .env
```

Open `.env` and configure your API key for the desired LLM provider (OpenAI, Google Gemini, Groq, or Ollama).

---

## 🧪 Testing the Agent in the Terminal

To start the interactive simulator:
```bash
python cli_test.py
```


---

## If finding trouble in one of these previous instructions try running
```bash
cd emporio_da_musica_agent
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe cli_test.py
```

## 🏗️ 2. Technical decisions

### Framework
Python with pip

### LLM
Google Gemini 3.8 Flash via
Google Anti-Gravity platform

### Project Structure
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

### Prompts

#### Initial Prompt
Build me a project of a text messages agent in python. This agent must work for whatsapp, and it is expected to talk to the costumers and give information and solve their problems if possible using the data from the company's products and polices (that I'm doing to provide once you build me a skeleton of the project). This agent must respond for the company Empório da Música.  
 The agen must:
▸  assume a personality aligned with the companies policies and expectation (more will be provided later). 
▸  Receive and answer messages with the available context given by the company.
▸  Consume company data (e.g.: availability, prices, sales, order status, etc) and 
company polices (e.g.: exchange polices, working hours, payment methods, etc). 
▸  Be able to handle correctly questions that get off the company provided data. 

Before building the app I would like to know a brief explanation of the steps you intend to build this app.

#### After first prompt
It was delivered the company's data and Gemini restructured the code. Some other prompts were made to 

#### User navigation prompt
about the user navigation in the agent, I would like it to address the most common types of questions customers make (“horários de funcionamento, status de pedido, preço e disponibilidade de produtos). First group these in major topics and then present the option to talk about those topics.

The navigation intended would be first a initial greeting, then after the asnwer of the customer it would try to resolve his problem and would add a follow up question regarding these major topics so to better solve the user problem. Remember to, wait until the max of 5 min for each response of the agent and no more. if the user asked more than 4 answers, ask if he is not finding the correct answer and offer the option for to get in contact with a human

#### Troubleshooting prompt
Some prompts were made to correct erros during simulation conversation and during environment configuration

## Known limitations
Time was the most important limitation in this project. To mitigate this the primary goal was having a running MVP so the workes can start using and in case the agent couldn't solve the costumer's problem to open a comunication with the humans workers. Later, with more time available, the primary goal is to improve messages and navigation to make it feel and sound natural human interaction and less robotic, as well receiving feedback from the employees on how to improve issues found by them.

Although Anti-Gravity was of vital importance in this project and doing mostly of the hard-working coding, I had to known exactly what I wanted and give flawless prompt instructions for the AI to get it write. It was a limitation for two reasons:
During my previous experiences with AI it has always been more effective to get the prompt right on first try (for that it requires clear visualization of what the project is about and how to make it) than to try to fix what it was already made;
Second due to credit/token limitation Gemini provides for their free users.

## Code Assistant AI
Google Anti-Gravity provides a platform specialy designed to code and build projects with the help of AI. I recently discovered this platform while I was enrolled in a Google Course which introduced new people to this platform and it has been a life changer!

### 3. User Interaction and Examples

#### User Navigation Flow and Customer Service Guidelines

The "Afinado" agent was designed following conversational UX best practices:

#### Initial Greeting and Introduction to the Main Topics

During the first interaction, the assistant welcomes the customer and presents the 4 main topics most frequently requested, allowing the customer to select a number or type their question in their own words:

🎸 1. Product Pricing and Availability (checking instruments in stock, brands, technical specifications, and a 5% discount for PIX payments)

📦 2. Order Status and Tracking (tracking deliveries using a tracking code or order number)

⏰ 3. Business Hours and Physical Store (store address in downtown Campo Grande/MS and business hours)

💳 4. Payment, Shipping, and Return Policies (interest-free installments, deliveries using the store's own motorcycle couriers, and returns under the Brazilian Consumer Protection Code (CDC) within 7 days)

#### 2. Problem Resolution + Follow-Up Question

When the customer submits a question:

The agent immediately resolves the issue using accurate catalog or policy information.

It then adds a contextual follow-up question related to the main topics to ensure a natural continuation of the conversation (e.g., after checking the price of a guitar, it asks whether the customer would like to calculate installment payments or shipping costs).

#### 3. Response Time (Maximum SLA of 5 Minutes)

Responses are generated promptly, complying with the company's operational guideline of a maximum response time of 5 minutes during business hours (Monday to Friday, 9 AM to 6 PM, and Saturdays, 9 AM to 1 PM).

#### 4. Proactive Human Handoff (4-Question Limit)

The system keeps track of conversation turns.

If the customer has already asked 4 or more questions, the agent empathetically checks whether they are finding the answers they need and proactively offers the option to speak directly with a human agent via WhatsApp (67) 3321-4500 or telephone (67) 3341-4444.

#### Examples

====================================================================
🎵 BEM-VINDO AO SIMULADOR DE CHAT DO EMPÓRIO DA MÚSICA 🎵
====================================================================
Assistente: Afinado (Consultor Virtual Musical)
Catálogo carregado: 65 produtos cadastrados
Pedidos na base: 20 pedidos
Políticas carregadas: ['sobre_a_empresa', 'horario_funcionamento', 'formas_pagamento', 'trocas_e_devolucoes', 'frete_e_entregas', 'promocoes_e_descontos', 'garantia', 'lgpd_e_privacidade', 'diretrizes_atendimento_whatsapp']

Comandos especiais:
  /catalog   -> Ver produtos do estoque
  /orders    -> Ver pedidos cadastrados para teste de rastreio
  /policies  -> Ver resumo das políticas da loja
  /clear     -> Limpar o histórico da conversa atual
  sair       -> Encerrar o simulador
====================================================================

Sugestões para testar o fluxo de navegação e atendimento:
  1. "Olá!" -> Menu inicial com os 4 Grandes Tópicos
  2. "Quais opções de violões disponíveis custando até R$1000?" -> Catálogo + follow-up
  3. "Onde fica a loja e qual o horário de funcionamento?" -> Localização + SLA
  4. "Quanto custa o Takamine GD20?" -> Preço + alerta de promoção vencida
  5. "Me arrependi da minha compra, posso devolver meu pedido?" -> Política de troca
  6. "Qual o status do meu pedido PED-1?" (ou rastreio "BRCX9876543BR")
  7. "Vocês vendem encordoamento ou palhetas?" -> Restrição de acessórios
  8. (A partir da 4ª pergunta): Teste de transbordo proativo para atendente humano!
--------------------------------------------------------------------

Você (Cliente): Vocês vendem encordoamento?

[Afinado está digitando...]

Afinado (WhatsApp):
Olá! 🎶 Aqui no *Empório da Música*, trabalhamos **exclusivamente com a venda de instrumentos musicais** (como violões, guitarras, baixos, teclados, baterias e instrumentos de sopro).

Por essa razão, **não comercializamos acessórios** como cordas, palhetas, cabos, pedais ou amplificadores. Para esses itens, recomendamos buscar uma loja parceira de acessórios da nossa região!

🎸 *Pergunta de acompanhamento:* Você gostaria de conhecer nossos modelos de violões ou guitarras em estoque, ou prefere consultar outro assunto?
--------------------------------------------------------------------

Você (Cliente): quais opções de violão vocês tem?

[Afinado está digitando...]

Afinado (WhatsApp):
🎶 Temos excelentes instrumentos em estoque no Empório da Música:

🎸 *Tagima Memphis AC-39 Nylon Natural*
• Preço de tabela: R$ 429.90
• À vista no PIX (5% off): *R$ 408.40*
• Estoque: 15 unidades disponíveis

🎸 *Rozini RC-104 Nylon Estudante*
• Preço de tabela: R$ 459.90
• À vista no PIX (5% off): *R$ 436.90*
• Estoque: 10 unidades disponíveis

🎸 *Shelby SN-100 Folk Aço Preto*
• Preço de tabela: R$ 549.00
• À vista no PIX (5% off): *R$ 521.55*
• Estoque: 5 unidades disponíveis

🎸 *Giannini GF-1R Aço Folk Sunburst*
• Preço de tabela: R$ 579.90
• À vista no PIX (5% off): *R$ 550.90*
• Estoque: 7 unidades disponíveis

💳 *Condições Comerciais:*
• Parcelamento no cartão em até 12x sem juros (ou até 3x sem valor mínimo de parcela).
• Frete grátis para compras acima de R$ 500 na região de Campo Grande/MS!

👉 *Acompanhamento:* Gostaria de saber mais sobre a ficha técnica de algum desses modelos ou consultar as opções de entrega?
--------------------------------------------------------------------

Você (Cliente): vocês vendem maquina de fazer macarrao?

[Afinado está digitando...]

Afinado (WhatsApp):
Olá! Seja muito bem-vindo ao *Empório da Música* em Campo Grande/MS! 🎶🎸

Sou o **Afinado**, seu consultor musical virtual. Para agilizar seu atendimento, aqui estão os principais tópicos em que posso te ajudar agora mesmo:

• 🎸 **1. Preço e Disponibilidade de Produtos**
  *(Consulte instrumentos em estoque, marcas, modelos e valores à vista no PIX com 5% off)*

• 📦 **2. Status e Rastreamento de Pedido**
  *(Acompanhe o envio do seu pedido pelo código de rastreamento ou número do pedido)*

• ⏰ **3. Horários de Funcionamento e Loja Física**
  *(Endereço no centro de Campo Grande/MS, expediente e canais de contato)*

• 💳 **4. Políticas de Pagamento, Frete e Devolução**
  *(Parcelamento em até 12x sem juros, frete grátis e direito de arrependimento em 7 dias)*

👉 Você pode escolher um dos números acima ou simplesmente digitar sua dúvida com suas próprias palavras!
--------------------------------------------------------------------

Você (Cliente): vocês vendem maquina de fazer macarrao?

[Afinado está digitando...]

Afinado (WhatsApp):
Olá! Seja muito bem-vindo ao *Empório da Música* em Campo Grande/MS! 🎶🎸

Sou o **Afinado**, seu consultor musical virtual. Para agilizar seu atendimento, aqui estão os principais tópicos em que posso te ajudar agora mesmo:

• 🎸 **1. Preço e Disponibilidade de Produtos**
  *(Consulte instrumentos em estoque, marcas, modelos e valores à vista no PIX com 5% off)*

• 📦 **2. Status e Rastreamento de Pedido**
  *(Acompanhe o envio do seu pedido pelo código de rastreamento ou número do pedido)*

• ⏰ **3. Horários de Funcionamento e Loja Física**
  *(Endereço no centro de Campo Grande/MS, expediente e canais de contato)*

• 💳 **4. Políticas de Pagamento, Frete e Devolução**
  *(Parcelamento em até 12x sem juros, frete grátis e direito de arrependimento em 7 dias)*

👉 Você pode escolher um dos números acima ou simplesmente digitar sua dúvida com suas próprias palavras!

---
💬 *Posso te ajudar com um especialista humano?*
Notei que já conversamos sobre vários pontos! Você está conseguindo encontrar todas as respostas que procura ou gostaria que eu te conectasse diretamente com a nossa equipe de atendimento presencial em Campo Grande?
• WhatsApp: **(67) 3321-4500** | Telefone: **(67) 3341-4444** (Seg-Sex 09h às 18h)
--------------------------------------------------------------------

Você (Cliente): sim

[Afinado está digitando...]

Afinado (WhatsApp):
Olá! Seja muito bem-vindo ao *Empório da Música* em Campo Grande/MS! 🎶🎸

Sou o **Afinado**, seu consultor musical virtual. Para agilizar seu atendimento, aqui estão os principais tópicos em que posso te ajudar agora mesmo:

• 🎸 **1. Preço e Disponibilidade de Produtos**
  *(Consulte instrumentos em estoque, marcas, modelos e valores à vista no PIX com 5% off)*

• 📦 **2. Status e Rastreamento de Pedido**
  *(Acompanhe o envio do seu pedido pelo código de rastreamento ou número do pedido)*

• ⏰ **3. Horários de Funcionamento e Loja Física**
  *(Endereço no centro de Campo Grande/MS, expediente e canais de contato)*

• 💳 **4. Políticas de Pagamento, Frete e Devolução**
  *(Parcelamento em até 12x sem juros, frete grátis e direito de arrependimento em 7 dias)*

👉 Você pode escolher um dos números acima ou simplesmente digitar sua dúvida com suas próprias palavras!

---
💬 *Posso te ajudar com um especialista humano?*
Notei que já conversamos sobre vários pontos! Você está conseguindo encontrar todas as respostas que procura ou gostaria que eu te conectasse diretamente com a nossa equipe de atendimento presencial em Campo Grande?
• WhatsApp: **(67) 3321-4500** | Telefone: **(67) 3341-4444** (Seg-Sex 09h às 18h)
--------------------------------------------------------------------






