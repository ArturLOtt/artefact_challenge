import json
import logging
from typing import Dict, Any, List
from app.config import settings
from app.knowledge.catalog import catalog_service
from app.knowledge.policies import policy_service
from app.knowledge.orders import order_service

logger = logging.getLogger(__name__)

# Tool schemas definitions for LLM Tool Calling
TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Busca instrumentos, equipamentos e acessórios no catálogo da loja por termo de busca, categoria ou preço máximo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca, por exemplo: 'violão', 'stratocaster', 'encordoamento', 'teclado yamaha', 'takamine'."
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoria específica: 'Cordas', 'Amplificadores', 'Teclas', 'Percussão', 'Acessórios'."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Preço máximo desejado em Reais (R$)."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Obtém detalhes completos de um produto específico através do seu código de identificação (ex: PROD-001).",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Código do produto (ex: PROD-001, PROD-002)."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Consulta o status, código de rastreamento e previsão de entrega de um pedido feito pelo cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Código do pedido fornecido pelo cliente (ex: PED-1001, PED-1002)."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_store_policy",
            "description": "Consulta informações e políticas da loja sobre tópicos específicos (horários, endereço, formas de pagamento, frete, trocas, garantia, lutheria).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": [
                            "physical_store",
                            "payment_methods",
                            "shipping_and_delivery",
                            "exchange_and_return_policy",
                            "luthier_services",
                            "human_attendant_support"
                        ],
                        "description": "Tópico sobre o qual deseja detalhes da política."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Registra uma solicitação de atendimento com um atendente humano e retorna o número direto de suporte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Motivo pelo qual o cliente precisa do atendente humano (ex: negociação especial, reclamação, dúvida técnica complexa)."
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

def execute_tool(name: str, args: Dict[str, Any]) -> str:
    """Dispatches tool execution and returns a JSON serialized string."""
    try:
        logger.info(f"Executing tool {name} with arguments: {args}")

        if name == "search_products":
            query = args.get("query")
            category = args.get("category")
            max_price = args.get("max_price")
            results = catalog_service.search(query=query, category=category, max_price=max_price)
            if not results:
                return json.dumps({
                    "status": "not_found",
                    "message": "Nenhum produto em estoque encontrado com os filtros informados.",
                    "available_categories": catalog_service.list_categories()
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "count": len(results), "products": results}, ensure_ascii=False)

        elif name == "get_product_details":
            product_id = args.get("product_id", "")
            product = catalog_service.get_by_id(product_id)
            if not product:
                return json.dumps({"status": "not_found", "message": f"Produto {product_id} não encontrado."}, ensure_ascii=False)
            return json.dumps({"status": "success", "product": product}, ensure_ascii=False)

        elif name == "track_order":
            order_id = args.get("order_id", "")
            order = order_service.get_by_id(order_id)
            if not order:
                return json.dumps({
                    "status": "not_found",
                    "message": f"Pedido {order_id} não localizado. Por favor, confirme o número do pedido."
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "order": order}, ensure_ascii=False)

        elif name == "get_store_policy":
            topic = args.get("topic", "")
            policy_data = policy_service.get_section(topic)
            if not policy_data:
                return json.dumps({
                    "status": "not_found",
                    "message": f"Tópico {topic} não encontrado nas políticas."
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "topic": topic, "policy": policy_data}, ensure_ascii=False)

        elif name == "escalate_to_human":
            reason = args.get("reason", "Solicitação do cliente")
            return json.dumps({
                "status": "escalated",
                "reason": reason,
                "support_phone": settings.HUMAN_SUPPORT_PHONE,
                "support_hours": "Segunda a Sexta das 09h às 18h",
                "instructions": "Informe ao cliente que ele pode chamar nossa equipe pelo número indicado para suporte humanizado."
            }, ensure_ascii=False)

        else:
            return json.dumps({"status": "error", "message": f"Ferramenta desconhecida: {name}"})

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return json.dumps({"status": "error", "message": str(e)})
