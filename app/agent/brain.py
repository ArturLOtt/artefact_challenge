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
        self._max_history = 12
        self._client: Optional[Any] = None
        self._init_client()

    def _init_client(self):
        """Initializes AsyncOpenAI client if API key is configured and library installed."""
        if AsyncOpenAI is None:
            self._client = None
            logger.info("OpenAI library not installed. Running in mock demonstration mode.")
            return

        api_key = settings.LLM_API_KEY.strip()
        is_placeholder = "your_" in api_key or api_key == ""
        if not is_placeholder:
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.LLM_BASE_URL
            )
        else:
            self._client = None
            logger.info(
                "LLM_API_KEY is using default placeholder. Running in demonstration fallback mode."
            )

    def get_or_create_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self._history:
            self._history[session_id] = [
                {"role": "system", "content": build_system_prompt()}
            ]
        return self._history[session_id]

    def clear_history(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]

    async def handle_message(self, session_id: str, user_text: str) -> str:
        """
        Main processing method. Receives a user message, manages history,
        executes necessary tool calls, and returns the agent's final text reply.
        """
        history = self.get_or_create_history(session_id)
        history.append({"role": "user", "content": user_text})

        # Trim history if too long, keeping the system prompt intact
        if len(history) > self._max_history + 1:
            history = [history[0]] + history[-self._max_history:]
            self._history[session_id] = history

        # If no valid API key is present, use intelligent local rule-based mock for testing
        if self._client is None:
            return await self._mock_fallback(user_text)

        try:
            # ReAct / Tool-calling loop
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

                # Append assistant message to history
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

                # If no tool calls were made, we have our final user response
                if not tool_calls:
                    return response_message.content or "Desculpe, não consegui processar a resposta no momento."

                # Execute requested tools
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

            # If max iterations reached, return fallback
            return "Estou com uma alta demanda de consultas no momento. Como posso te ajudar pontualmente?"

        except Exception as e:
            logger.error(f"Error in LLM handle_message: {e}", exc_info=True)
            return (
                "Desculpe, tive uma oscilação técnica momentânea. "
                f"Se preferir, você pode falar direto com nossa equipe pelo WhatsApp {settings.HUMAN_SUPPORT_PHONE}!"
            )

    async def _mock_fallback(self, user_text: str) -> str:
        """
        Local simulation engine when LLM_API_KEY is not yet supplied.
        Allows testing the tools and persona directly from the terminal or test suite.
        """
        text = user_text.lower()

        # Out-of-bounds guardrail simulation
        out_of_scope_keywords = ["receita", "futebol", "política", "politica", "carro", "imóvel", "programação", "python", "geladeira"]
        if any(w in text for w in out_of_scope_keywords):
            return (
                "Olá! 🎶 Como assistente do Empório da Música, meu foco é exclusivamente te ajudar "
                "com instrumentos musicais, equipamentos de som, acessórios e serviços da nossa loja!\n\n"
                "Posso te ajudar a encontrar algum instrumento ou tirar dúvidas sobre nossos produtos hoje? 🎸"
            )

        # Human attendant request
        if "humano" in text or "atendente" in text or "falar com alguém" in text:
            tool_res = json.loads(execute_tool("escalate_to_human", {"reason": "Solicitação direta de atendente"}))
            return (
                f"Com certeza! Você pode falar diretamente com nossa equipe de atendimento humanizado "
                f"pelo WhatsApp: {tool_res['support_phone']} 💬\n\n"
                f"Horário de atendimento: {tool_res['support_hours']}. Fique à vontade para nos chamar lá!"
            )

        # Order tracking simulation
        if "pedido" in text or "ped-" in text or "rastre" in text:
            import re
            match = re.search(r"ped-\d+", text, re.IGNORECASE)
            order_id = match.group(0).upper() if match else "PED-1002"
            tool_res = json.loads(execute_tool("track_order", {"order_id": order_id}))
            if tool_res.get("status") == "success":
                ord_data = tool_res["order"]
                return (
                    f"📦 *Status do Pedido {ord_data['order_id']}*:\n"
                    f"• Cliente: {ord_data['customer_name']}\n"
                    f"• Status: *{ord_data['status']}*\n"
                    f"• Transportadora: {ord_data.get('carrier', 'N/A')}\n"
                    f"• Rastreio: {ord_data.get('tracking_code') or 'Em processamento'}\n"
                    f"• Observações: {ord_data.get('notes', '')}\n\n"
                    f"Se precisar de mais detalhes, estou à disposição!"
                )
            else:
                return f"Não localizei o pedido informado ({order_id}). Por favor, confira o código digitado (ex: PED-1001)!"

        # Policy inquiries
        if any(w in text for w in ["troca", "devolu", "garantia", "defeito"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "exchange_and_return_policy"}))
            p = tool_res.get("policy", {})
            return (
                "🔄 *Políticas de Troca e Garantia - Empório da Música*:\n"
                f"• *Arrependimento:* {p.get('right_of_regret')}\n"
                f"• *Defeito:* {p.get('defect_exchange')}\n"
                f"• *Garantia:* {p.get('warranty')}\n\n"
                "Todos os nossos instrumentos passam por checagem antes do envio! 🎸"
            )

        if any(w in text for w in ["pagamento", "parcela", "pix", "cartão", "cartao"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "payment_methods"}))
            p = tool_res.get("policy", {})
            return (
                "💳 *Formas de Pagamento no Empório da Música*:\n"
                f"• *PIX:* {p.get('pix')}\n"
                f"• *Cartão de Crédito:* {p.get('credit_card')}\n"
                f"• *Boleto Bancário:* {p.get('bank_slip')}\n"
            )

        if any(w in text for w in ["horário", "horario", "endereço", "endereco", "onde fica", "loja física"]):
            tool_res = json.loads(execute_tool("get_store_policy", {"topic": "physical_store"}))
            p = tool_res.get("policy", {})
            hours = p.get("business_hours", {})
            return (
                "📍 *Nossa Loja Física*:\n"
                f"• Endereço: {p.get('address')}\n"
                f"• Horários:\n"
                f"  - Seg a Sex: {hours.get('weekdays')}\n"
                f"  - Sábados: {hours.get('saturdays')}\n"
                f"  - Domingos e Feriados: {hours.get('sundays_and_holidays')}\n"
                f"• Estacionamento: {p.get('parking')}\n\n"
                "Venha tomar um café e testar nossos instrumentos! ☕🎸"
            )

        # Product search simulation
        search_term = None
        for cand in ["violão", "violao", "guitarra", "teclado", "bateria", "amplificador", "palheta", "cabo", "afinador", "corda"]:
            if cand in text:
                search_term = cand
                break

        query = search_term or "violão"
        tool_res = json.loads(execute_tool("search_products", {"query": query}))
        if tool_res.get("status") == "success":
            items = tool_res["products"][:3]
            resp = f"🎶 Encontrei opções incríveis de *{query.capitalize()}* para você no Empório da Música:\n\n"
            for item in items:
                resp += (
                    f"🎸 *{item['name']}*\n"
                    f"• Marca: {item['brand']}\n"
                    f"• Preço: R$ {item['price']:.2f} (ou R$ {item['discount_price']:.2f} no PIX)\n"
                    f"• Estoque: {item['stock']} unidades\n"
                    f"• Indicação: {item['suitable_for']}\n\n"
                )
            resp += "Gostaria de saber mais detalhes sobre algum desses modelos ou prefere ver outras opções?"
            return resp

        return (
            "Olá! Seja muito bem-vindo ao *Empório da Música*! 🎶\n\n"
            "Sou o Afinado, seu consultor musical virtual. Posso te ajudar com:\n"
            "• Consulta de instrumentos e acessórios em estoque\n"
            "• Preços, promoções e formas de pagamento\n"
            "• Rastreamento do seu pedido\n"
            "• Horários, endereço da nossa loja e políticas de troca\n\n"
            "Como posso te ajudar a encontrar o timbre perfeito hoje?"
        )

agent_brain = AgentBrain()
