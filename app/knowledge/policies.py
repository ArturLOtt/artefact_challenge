import json
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class PolicyService:
    def __init__(self, file_path=None):
        self.file_path = file_path or settings.POLICIES_FILE
        self._policies: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Reload store policies from JSON file."""
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._policies = json.load(f)
                logger.info(f"Loaded policies from {self.file_path}")
            else:
                logger.warning(f"Policies file not found at: {self.file_path}")
                self._policies = {}
        except Exception as e:
            logger.error(f"Error loading policies file: {e}")
            self._policies = {}

    def get_all(self) -> Dict[str, Any]:
        return self._policies

    def get_section(self, section_name: str) -> Optional[Any]:
        """Fetch a specific section (e.g., payment_methods, exchange_and_return_policy, etc.)."""
        return self._policies.get(section_name)

    def get_summary_text(self) -> str:
        """Generates a synthesized text summary of policies for persona context."""
        if not self._policies:
            return "Políticas da loja não carregadas."

        store = self._policies.get("physical_store", {})
        hours = store.get("business_hours", {})
        payments = self._policies.get("payment_methods", {})
        shipping = self._policies.get("shipping_and_delivery", {})
        returns = self._policies.get("exchange_and_return_policy", {})
        luthier = self._policies.get("luthier_services", {})

        return (
            f"--- POLÍTICAS E INFORMAÇÕES DO EMPÓRIO DA MÚSICA ---\n"
            f"• Endereço: {store.get('address', 'Não informado')}\n"
            f"• Horários: Seg-Sex {hours.get('weekdays', '')} | Sáb: {hours.get('saturdays', '')} | Domingo: {hours.get('sundays_and_holidays', '')}\n"
            f"• Pagamentos: PIX (5% off à vista) | Cartão até 10x sem juros | Boleto à vista\n"
            f"• Frete e Entrega: Frete grátis para SP acima de R$ 299 | Envio para todo o Brasil via Correios e Transportadoras | Retirada na loja em 2h\n"
            f"• Trocas e Devoluções: 7 dias para arrependimento (CDC) | 30 dias para troca por defeito na loja | 90 dias de garantia legal + garantia do fabricante\n"
            f"• Serviços de Luthieria: Oficina própria na loja física para regulagem, troca de cordas e reparos. Todo instrumento comprado sai com regulagem inicial cortesia!\n"
            f"• Suporte Humano: Disponível via WhatsApp no número {self._policies.get('human_attendant_support', {}).get('whatsapp_channel', settings.HUMAN_SUPPORT_PHONE)}\n"
        )

policy_service = PolicyService()
