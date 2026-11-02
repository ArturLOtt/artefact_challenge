import json
import logging
from typing import Dict, Any, List
from app.knowledge.catalog import catalog_service
from app.knowledge.policies import policy_service
from app.knowledge.orders import order_service

logger = logging.getLogger(__name__)

TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Busca instrumentos musicais no catálogo da loja por termo de pesquisa (ex: 'violão', 'tagima', 'yamaha', 'teclado', 'baixo'), categoria (ex: 'Violões', 'Guitarras', 'Baixos', 'Teclados e Pianos', 'Baterias e Percussão', 'Instrumentos de Sopro (Madeiras)', 'Instrumentos de Sopro (Metais)', 'Cordas Orquestrais', 'Ukuleles') ou preço máximo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca textual."
                    },
                    "category": {
                        "type": "string",
                        "description": "Nome da categoria."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Preço máximo em reais."
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "Filtra apenas produtos com estoque disponível."
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
            "description": "Consulta ficha técnica completa, preço de tabela, preço com desconto no PIX (5%), estoque e promoções de um instrumento específico pelo nome ou ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Nome do instrumento ou código de identificação (ex: 'Takamine GD20', 'Yamaha C40', '81')."
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Rastreia o pedido de um cliente através do número do pedido (ex: '1', 'PED-1', 'PED-1002') ou pelo código de rastreamento (ex: 'BRCX9876543BR').",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Número do pedido ou código de rastreio."
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_store_policy",
            "description": "Consulta seções específicas do manual de políticas e procedimentos do Empório da Música (horários, endereço, formas de pagamento, parcelamento, frete, trocas, devoluções, garantia, restrição de acessórios, LGPD).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": [
                            "sobre_a_empresa",
                            "horario_funcionamento",
                            "formas_pagamento",
                            "trocas_e_devolucoes",
                            "frete_e_entregas",
                            "promocoes_e_descontos",
                            "garantia",
                            "diretrizes_atendimento_whatsapp"
                        ],
                        "description": "Seção do manual de políticas desejada."
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
            "description": "Aciona o protocolo de transbordo para atendimento humano da equipe em Campo Grande/MS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Motivo do encaminhamento."
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

def execute_tool(name: str, args: Dict[str, Any]) -> str:
    try:
        logger.info(f"Executing tool {name} with arguments: {args}")

        if name == "search_products":
            query = args.get("query")
            category = args.get("category")
            max_price = args.get("max_price")
            in_stock_only = args.get("in_stock_only", True)

            results = catalog_service.search_products(
                query=query,
                category=category,
                max_price=max_price,
                in_stock_only=in_stock_only
            )

            if not results:
                return json.dumps({
                    "status": "not_found",
                    "message": "Nenhum instrumento em estoque encontrado com os critérios informados.",
                    "categories_available": [c["name"] for c in catalog_service.list_categories()]
                }, ensure_ascii=False)

            return json.dumps({
                "status": "success",
                "total_found": len(results),
                "products": results
            }, ensure_ascii=False)

        elif name == "get_product_details":
            identifier = args.get("identifier") or args.get("product_id") or ""
            product = catalog_service.get_product_details(str(identifier))
            if not product:
                return json.dumps({
                    "status": "not_found",
                    "message": f"Instrumento '{identifier}' não encontrado no catálogo."
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "product": product}, ensure_ascii=False)

        elif name == "track_order":
            identifier = args.get("identifier") or args.get("order_id") or ""
            order = order_service.track_order(str(identifier))
            if not order:
                return json.dumps({
                    "status": "not_found",
                    "message": f"Pedido ou código de rastreamento '{identifier}' não localizado no sistema."
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "order": order}, ensure_ascii=False)

        elif name == "get_store_policy":
            topic = args.get("topic", "")
            policy_data = policy_service.get_section(topic)
            if not policy_data:
                return json.dumps({
                    "status": "not_found",
                    "message": f"Tópico '{topic}' não encontrado nas políticas."
                }, ensure_ascii=False)
            return json.dumps({"status": "success", "topic": topic, "policy": policy_data}, ensure_ascii=False)

        elif name == "escalate_to_human":
            reason = args.get("reason", "Solicitação do cliente")
            return json.dumps({
                "status": "escalated",
                "reason": reason,
                "whatsapp_support": "(67) 3321-4500",
                "phone_support": "(67) 3341-4444",
                "working_hours": "Segunda a Sexta das 09:00 às 18:00 | Sábado das 09:00 às 13:00",
                "address": "Rua 14 de Maio, 3200 — Centro, Campo Grande - MS",
                "instructions": "Informe com simpatia os contatos acima para o atendimento humanizado com nossa equipe."
            }, ensure_ascii=False)

        else:
            return json.dumps({"status": "error", "message": f"Ferramenta desconhecida: {name}"})

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": str(e)})
