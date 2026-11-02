import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PolicyService:
    def __init__(self, file_path: Optional[Path] = None):
        base_path = Path(__file__).resolve().parent.parent.parent
        candidates = [
            base_path / "data" / "politicas_da_loja.json",
            base_path / "data" / "policies.json"
        ]
        self.file_path = None
        for cand in candidates:
            if cand.exists():
                self.file_path = cand
                break
        if self.file_path is None:
            self.file_path = candidates[0]

        self._policies: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._policies = json.load(f)
                logger.info(f"Loaded store policies successfully from {self.file_path}")
            else:
                logger.warning(f"Policies file not found at {self.file_path}")
                self._policies = {}
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            self._policies = {}

    def get_all(self) -> Dict[str, Any]:
        return self._policies

    def get_section(self, section: str) -> Optional[Any]:
        return self._policies.get(section)

    def get_summary_text(self) -> str:
        emp = self._policies.get("sobre_a_empresa", {})
        hor = self._policies.get("horario_funcionamento", {})
        pag = self._policies.get("formas_pagamento", {})
        tro = self._policies.get("trocas_e_devolucoes", {})
        fre = self._policies.get("frete_e_entregas", {})
        gar = self._policies.get("garantia", {})

        return f"""=== POLÍTICAS E REGRAS OFICIAIS DO EMPÓRIO DA MÚSICA (CAMPO GRANDE/MS) ===
• LOCALIZAÇÃO: {emp.get('endereco', 'Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333')}
• CONTATO: Telefone (67) 3341-4444 | WhatsApp Atendimento (67) 3321-4500 | E-mail: {emp.get('email', 'contato@emporiodamusica.com.br')}
• HORÁRIOS: Segunda a Sexta {hor.get('segunda_a_sexta', '09:00 às 18:00')} | Sábado {hor.get('sabado', '09:00 às 13:00')} | Domingos e Feriados: Fechado.
• TEMPO DE RESPOSTA (SLA): Máximo de 5 minutos durante o horário de funcionamento. Fora do expediente, informar retorno no próximo dia útil.
• ESCOPO RESTRITO: A loja comercializa EXCLUSIVAMENTE instrumentos musicais. NÃO vendemos acessórios (cordas, palhetas, cabos, cases, pedais, amplificadores). Quando solicitados, informar educadamente e sugerir lojas parceiras.
• PAGAMENTO:
  - PIX: 5% de desconto sobre o preço de tabela (NÃO cumulativo com promoções).
  - Cartão de Débito: à vista.
  - Cartão de Crédito: até 12x sem juros (até 3x s/ valor mínimo acima de R$ 50; 4x-6x parcela mín R$ 80; 7x-12x parcela mín R$ 100).
  - Pagamento Misto (PIX + Cartão): permitido apenas para compras acima de R$ 2.000,00.
  - Boleto Bancário: à vista, compensação até 3 dias úteis.
• FRETES E ENTREGAS:
  - Campo Grande (Região Metropolitana): Frete Grátis acima de R$ 500. Abaixo de R$ 500, taxa fixa de R$ 35,00. Prazo: 1 a 3 dias úteis (motoboy próprio).
  - Outras cidades: Correios (PAC 5-12 dias úteis, SEDEX 2-5 dias úteis) e Jadlog (3-8 dias úteis). Código padrão: BR + 9 alfanuméricos + BR.
• TROCAS E DEVOLUÇÕES:
  - Arrependimento (compras online): até 7 dias corridos após o recebimento, produto lacrado/sem uso na embalagem original, reembolso em até 10 dias úteis. Frete por conta da loja.
  - Troca por Defeito: até 30 dias corridos na loja. Após 30 dias, acionar garantia do fabricante.
  - Troca por Preferência: até 7 dias corridos se houver estoque e embalagem original intacta.
  - NÃO elegíveis: instrumentos com regulagem/setup personalizado sob encomenda, produtos em liquidação ("venda final") e boquilhas de sopro (higiene).
• PROMOÇÕES EXPIRADAS: Se o cliente perguntar de uma promoção vencida, informar com transparência que ela já encerrou e indicar o preço regular atual. NUNCA prometer desconto expirado.
• GARANTIA: 90 dias de garantia legal (CDC) contra defeitos de fabricação + garantia do fabricante (6 a 24 meses). Não cobre desgaste natural ou mau uso.
• ATENDIMENTO HUMANO: WhatsApp (67) 3321-4500 ou telefone (67) 3341-4444 (Seg-Sex das 09h às 18h).
"""

policy_service = PolicyService()
