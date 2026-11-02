import json
import logging
from typing import Dict, List, Any, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from app.config import settings
from app.agent.persona import build_system_prompt
from app.agent.tools import TOOLS_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

class AgentBrain:
    def __init__(self):
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._turn_counts: Dict[str, int] = {}
        self._max_history = 14
        self._client: Optional[Any] = None
        self._init_client()

    def _init_client(self):
        """Initializes AsyncOpenAI client if API key is provided and library is installed."""
        if AsyncOpenAI is None:
            self._client = None
            logger.info("OpenAI library not installed. Running in local simulation mode.")
            return

        api_key = settings.LLM_API_KEY.strip()
        is_placeholder = "your_" in api_key or api_key == ""
        if not is_placeholder:
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.LLM_BASE_URL
            )
            logger.info(f"LLM client initialized with model '{settings.LLM_MODEL}' at {settings.LLM_BASE_URL}")
        else:
            self._client = None
            logger.info("LLM_API_KEY is placeholder. Running in demonstration fallback mode.")

    def get_or_create_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self._history:
            self._history[session_id] = [
                {"role": "system", "content": build_system_prompt()}
            ]
            self._turn_counts[session_id] = 0
        return self._history[session_id]

    def clear_history(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]
        if session_id in self._turn_counts:
            del self._turn_counts[session_id]

    def get_turn_count(self, session_id: str) -> int:
        return self._turn_counts.get(session_id, 0)

    async def handle_message(self, session_id: str, user_text: str) -> str:
        """
        Receives user message, manages session turn count, triggers LLM with tool calling,
        and enforces user navigation with contextual follow-ups and human escalation after 4 turns.
        """
        history = self.get_or_create_history(session_id)
        self._turn_counts[session_id] = self._turn_counts.get(session_id, 0) + 1
        turn_count = self._turn_counts[session_id]

        history.append({"role": "user", "content": user_text})

        # Inject turn guidance when user has asked 4 or more questions
        if turn_count >= 4:
            history.append({
                "role": "system",
                "content": (
                    f"[DIRETRIZ DE NAVEGAÇÃO]: O cliente já fez {turn_count} perguntas nesta sessão. "
                    "Após responder à pergunta atual, pergunte proativamente com empatia se ele está conseguindo "
                    "encontrar a resposta correta ou se prefere ser transferido para um atendente humano "
                    "no WhatsApp: (67) 3321-4500 ou telefone (67) 3341-4444."
                )
            })

        # Trim history while keeping system prompt intact
        if len(history) > self._max_history + 2:
            history = [history[0]] + history[-self._max_history:]
            self._history[session_id] = history

        # Local simulation fallback if no API key is configured
        if self._client is None:
            return await self._mock_fallback(session_id, user_text, turn_count)

        try:
            max_iterations = 5
            for _ in range(max_iterations):
                response = await self._client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=history,
                    tools=TOOLS_DEFINITIONS,
                    tool_choice="auto",
                    temperature=settings.TEMPERATURE
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                assistant_record = {
                    "role": "assistant",
                    "content": response_message.content or ""
                }
                if tool_calls:
                    assistant_record["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                history.append(assistant_record)

                if not tool_calls:
                    return response_message.content or "Olá! Como posso ajudar você hoje no Empório da Música?"

                # Execute all requested tools
                for tc in tool_calls:
                    func_name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except Exception:
                        args = {}

                    tool_output = execute_tool(func_name, args)

                    history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_output
                    })

            return "Tivemos muitas consultas simultâneas no sistema. Posso te ajudar com outra dúvida sobre nossos instrumentos?"

        except Exception as e:
            logger.error(f"Error in LLM handle_message: {e}", exc_info=True)
            return (
                "Desculpe, tive uma oscilação técnica momentânea. "
                "Você pode falar diretamente com nossa equipe em Campo Grande pelo WhatsApp: (67) 3321-4500!"
            )

    async def _mock_fallback(self, session_id: str, user_text: str, turn_count: int) -> str:
        """
        Smart offline simulation engine.
        Applies major topic grouping, problem resolution, contextual follow-ups,
        and human escalation after 4 questions.
        """
        text = user_text.lower().strip()

        # Human transfer check suffix if user has asked 4 or more questions
        human_offer_suffix = ""
        if turn_count >= 4:
            human_offer_suffix = (
                "\n\n---\n💬 *Posso te ajudar com um especialista humano?*\n"
                "Notei que já conversamos sobre vários pontos! Você está conseguindo encontrar todas as respostas que procura "
                "ou gostaria que eu te conectasse diretamente com a nossa equipe de atendimento presencial em Campo Grande?\n"
                "• WhatsApp: **(67) 3321-4500** | Telefone: **(67) 3341-4444** (Seg-Sex 09h às 18h)"
            )

        # 1. SCOPE RESTRICTION - ACCESSORIES (cordas, palhetas, cabos, cases, pedais, amplificadores)
        accessory_keywords = ["corda", "encordoamento", "palheta", "cabo", "case", "capa", "pedal", "amplificador", "amp "]
        if any(w in text for w in accessory_keywords):
            return (
                "Olá! 🎶 Aqui no *Empório da Música*, trabalhamos **exclusivamente com a venda de instrumentos musicais** "
                "(como violões, guitarras, baixos, teclados, baterias e instrumentos de sopro).\n\n"
                "Por essa razão, **não comercializamos acessórios** como cordas, palhetas, cabos, pedais ou amplificadores. "
                "Para esses itens, recomendamos buscar uma loja parceira de acessórios da nossa região!\n\n"
                "🎸 *Pergunta de acompanhamento:* Você gostaria de conhecer nossos modelos de violões ou guitarras em estoque, ou prefere consultar outro assunto?"
                f"{human_offer_suffix}"
            )

        # 2. OFF-TOPIC GUARDRAIL (receitas, carros, política, programação, geladeiras)
        off_topic_words = ["receita", "futebol", "política", "politica", "carro", "imóvel", "programação", "python", "geladeira", "lavar roupa"]
        if any(w in text for w in off_topic_words):
            return (
                "Olá! 🎶 Como consultor virtual do *Empório da Música*, meu foco é exclusivamente ajudar você "
                "com nossos instrumentos musicais, pedidos e informações da nossa loja em Campo Grande/MS!\n\n"
                "Podemos falar sobre:\n"
                "• 🎸 **1. Preço e disponibilidade de instrumentos**\n"
                "• 📦 **2. Rastreamento de pedidos**\n"
                "• ⏰ **3. Horários da loja física**\n"
                "• 💳 **4. Políticas de pagamento, frete e trocas**\n\n"
                "Sobre qual desses temas posso te ajudar hoje?"
                f"{human_offer_suffix}"
            )

        # 3. DIRECT HUMAN ESCALATION REQUEST
        if any(w in text for w in ["humano", "atendente", "falar com alguém", "pessoa"]):
            tool_res = json.loads(execute_tool("escalate_to_human", {"reason": "Solicitação do cliente"}))
            return (
                "Com certeza! Você pode falar diretamente com a nossa equipe de atendimento em Campo Grande/MS:\n\n"
                f"💬 *WhatsApp:* {tool_res['whatsapp_support']}\n"
                f"📞 *Telefone Fixo:* {tool_res['phone_support']}\n"
                f"⏰ *Horário:* {tool_res['working_hours']}\n"
                f"📍 *Endereço:* {tool_res['address']}\n\n"
                "Nossa equipe terá o maior prazer em te atender pessoalmente! 🎶"
            )

        # 4. ORDER TRACKING (Status e Rastreamento de Pedido)
        if any(w in text for w in ["pedido", "ped-", "rastre", "brcx", "brab", "brdz", "brqm"]):
            import re
            match = re.search(r"ped-\d+|\b\d+\b|BR[A-Z0-9]+BR", text, re.IGNORECASE)
            order_id = match.group(0).upper() if match else "1"
            tool_res = json.loads(execute_tool("track_order", {"identifier": order_id}))
            if tool_res.get("status") == "success":
                ord_data = tool_res["order"]
                items_str = "\n".join([f"  • {it['quantity']}x {it['name']} (R$ {it['unit_price']:.2f})" for it in ord_data["items"]])
                return (
                    f"📦 *Status do Pedido {ord_data['order_id']}*:\n"
                    f"• Cliente: {ord_data['customer_name']} ({ord_data['city']})\n"
                    f"• Data da Compra: {ord_data['order_date']}\n"
                    f"• Status Atual: *{ord_data['status']}*\n"
                    f"• Rastreamento: {ord_data['tracking_code'] or 'Em processamento / Motoboy próprio'}\n"
                    f"• Previsão de Entrega: {ord_data['estimated_delivery'] or 'A confirmar'}\n"
                    f"• Itens Comprados:\n{items_str}\n"
                    f"• Total: R$ {ord_data['total_brl']:.2f} ({ord_data['payment_method']})\n\n"
                    "👉 *Acompanhamento:* Gostaria de saber mais detalhes sobre os prazos de entrega para sua cidade ou sobre as nossas políticas de garantia e troca?"
                    f"{human_offer_suffix}"
                )
            else:
                return (
                    f"Não localizei nenhum pedido com o código '{order_id}'. Por favor, confira o número informado (ex: PED-1 ou o código BR...BR).\n\n"
                    "👉 Gostaria de tentar outro código ou prefere que eu verifique diretamente com um atendente humano?"
                    f"{human_offer_suffix}"
                )

        # 5. SPECIFIC PRODUCT & PROMOTION (E.g. Takamine GD20)
        if "takamine" in text or "gd20" in text:
            tool_res = json.loads(execute_tool("get_product_details", {"identifier": "Takamine GD20"}))
            if tool_res.get("status") == "success":
                p = tool_res["product"]
                expired_info = ""
                if p.get("expired_promotions"):
                    exp = p["expired_promotions"][0]
                    expired_info = (
                        f"\n⚠️ *Nota sobre promoções:* A campanha '{exp['description']}' com {exp['discount_percent']:.0f}% de desconto "
                        "já foi encerrada. O valor atual vigente é o preço de tabela normal."
                    )
                return (
                    f"🎸 *{p['name']}*\n"
                    f"• Preço de tabela: *R$ {p['price']:.2f}*\n"
                    f"• À vista no PIX (5% de desconto de tabela): *R$ {p['pix_price']:.2f}*\n"
                    f"• Cartão de crédito: até 12x de R$ {p['price']/12:.2f} sem juros\n"
                    f"• Estoque disponível: {p['stock']} unidades\n"
                    f"• Especificações: {p['description']}"
                    f"{expired_info}\n\n"
                    "👉 *Acompanhamento:* Como o valor ultrapassa R$ 500, o frete é grátis para a região de Campo Grande/MS! "
                    "Gostaria de consultar as condições de frete para outra cidade ou simular parcelamento?"
                    f"{human_offer_suffix}"
                )

        # 6. PRODUCT CATALOG QUERY (Preço e Disponibilidade de Produtos)
        if any(w in text for w in ["viol", "guitarra", "baixo", "teclado", "piano", "bateria", "sopro", "ukulele"]):
            category = "Violões" if "viol" in text else None
            max_price = 1000.0 if ("1000" in text or "mil" in text) else None

            tool_res = json.loads(execute_tool("search_products", {
                "query": "",
                "category": category,
                "max_price": max_price,
                "in_stock_only": True
            }))

            if tool_res.get("status") == "success":
                prods = tool_res["products"]
                hdr = "opções de violões disponíveis custando até R$ 1.000,00" if max_price else "instrumentos em estoque"
                msg = f"🎶 Temos excelentes {hdr} no Empório da Música:\n\n"
                for pr in prods[:4]:
                    msg += (
                        f"🎸 *{pr['name']}*\n"
                        f"• Preço de tabela: R$ {pr['price']:.2f}\n"
                        f"• À vista no PIX (5% off): *R$ {pr['pix_price']:.2f}*\n"
                        f"• Estoque: {pr['stock']} unidades disponíveis\n\n"
                    )
                msg += (
                    "💳 *Condições Comerciais:*\n"
                    "• Parcelamento no cartão em até 12x sem juros (ou até 3x sem valor mínimo de parcela).\n"
                    "• Frete grátis para compras acima de R$ 500 na região de Campo Grande/MS!\n\n"
                    "👉 *Acompanhamento:* Gostaria de saber mais sobre a ficha técnica de algum desses modelos ou consultar as opções de entrega?"
                )
                return msg + human_offer_suffix

        # 7. STORE POLICIES (Trocas, Devoluções, Arrependimento, Pagamento)
        if any(w in text for w in ["arrepende", "devolver", "troca", "devolu"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "trocas_e_devolucoes"}))
            tro = tool_res.get("policy", {})
            arr = tro.get("direito_de_arrependimento", {})
            return (
                "🔄 *Política de Devolução e Arrependimento - Empório da Música*:\n\n"
                f"Sim, você pode devolver o produto! Conforme o Código de Defesa do Consumidor para compras online:\n"
                f"• *Prazo:* {arr.get('prazo')}\n"
                f"• *Condições:* {arr.get('condicoes')}\n"
                f"• *Reembolso:* {arr.get('reembolso')}\n"
                f"• *Frete de devolução:* {arr.get('frete')}\n\n"
                "👉 *Acompanhamento:* Você gostaria de informar o número do seu pedido para iniciarmos o processo ou prefere consultar prazos de garantia?"
                f"{human_offer_suffix}"
            )

        if any(w in text for w in ["pagamento", "parcela", "pix", "cartão", "cartao", "boleto"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "formas_pagamento"}))
            pag = tool_res.get("policy", {})
            return (
                "💳 *Formas de Pagamento no Empório da Música*:\n\n"
                f"• *PIX:* 5% de desconto à vista sobre o preço de tabela (não cumulativo com promoções).\n"
                f"• *Cartão de Crédito:* em até 12x sem juros (até 3x s/ parcela mínima acima de R$ 50; 4x-6x mín R$ 80; 7x-12x mín R$ 100).\n"
                f"• *Boleto Bancário:* à vista com compensação em até 3 dias úteis.\n"
                f"• *Pagamento Misto (PIX + Cartão):* disponível para compras a partir de R$ 2.000,00.\n\n"
                "👉 *Acompanhamento:* Deseja simular o valor das parcelas para algum instrumento específico?"
                f"{human_offer_suffix}"
            )

        # 8. STORE LOCATION & HOURS (Horários de funcionamento)
        if any(w in text for w in ["endereço", "endereco", "onde fica", "horário", "horario", "localiza"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "sobre_a_empresa"}))
            p_emp = tool_res.get("policy", {})
            tool_hor = json.loads(execute_tool("get_store_policy", {"topic": "horario_funcionamento"}))
            p_hor = tool_hor.get("policy", {})
            return (
                "📍 *Empório da Música - Localização e Horários*:\n\n"
                f"• *Endereço:* {p_emp.get('endereco')}\n"
                f"• *Telefone:* {p_emp.get('telefone_fixo')} | WhatsApp: {p_emp.get('whatsapp_atendimento')}\n"
                f"• *Expediente da Loja:*\n"
                f"  - Segunda a Sexta: {p_hor.get('segunda_a_sexta')}\n"
                f"  - Sábado: {p_hor.get('sabado')}\n"
                f"  - Domingos e Feriados: Fechado\n"
                f"• *Tempo de Resposta:* Nosso assistente atende imediatamente com tempo médio de resposta de até 5 minutos durante o horário de expediente!\n\n"
                "👉 *Acompanhamento:* Você está procurando algum instrumento específico para vir testar pessoalmente na loja?"
                f"{human_offer_suffix}"
            )

        # 9. INITIAL GREETING WITH MAJOR TOPICS GROUPING
        return (
            "Olá! Seja muito bem-vindo ao *Empório da Música* em Campo Grande/MS! 🎶🎸\n\n"
            "Sou o **Afinado**, seu consultor musical virtual. Para agilizar seu atendimento, "
            "aqui estão os principais tópicos em que posso te ajudar agora mesmo:\n\n"
            "• 🎸 **1. Preço e Disponibilidade de Produtos**\n"
            "  *(Consulte instrumentos em estoque, marcas, modelos e valores à vista no PIX com 5% off)*\n\n"
            "• 📦 **2. Status e Rastreamento de Pedido**\n"
            "  *(Acompanhe o envio do seu pedido pelo código de rastreamento ou número do pedido)*\n\n"
            "• ⏰ **3. Horários de Funcionamento e Loja Física**\n"
            "  *(Endereço no centro de Campo Grande/MS, expediente e canais de contato)*\n\n"
            "• 💳 **4. Políticas de Pagamento, Frete e Devolução**\n"
            "  *(Parcelamento em até 12x sem juros, frete grátis e direito de arrependimento em 7 dias)*\n\n"
            "👉 Você pode escolher um dos números acima ou simplesmente digitar sua dúvida com suas próprias palavras!"
            f"{human_offer_suffix}"
        )

agent_brain = AgentBrain()
