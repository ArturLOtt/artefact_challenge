import json
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, file_path=None):
        self.file_path = file_path or settings.ORDERS_FILE
        self._orders: List[Dict[str, Any]] = []
        self.reload()

    def reload(self) -> None:
        """Reload orders database from JSON file."""
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._orders = json.load(f)
                logger.info(f"Loaded {len(self._orders)} orders from {self.file_path}")
            else:
                logger.warning(f"Orders file not found at: {self.file_path}")
                self._orders = []
        except Exception as e:
            logger.error(f"Error loading orders file: {e}")
            self._orders = []

    def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Find order by code (e.g. PED-1001)."""
        oid = order_id.strip().upper()
        for order in self._orders:
            if order.get("order_id", "").upper() == oid:
                return order
        return None

    def get_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """Find orders associated with a phone number (normalized digits)."""
        clean_phone = "".join(filter(str.isdigit, phone))
        results = []
        for order in self._orders:
            order_phone = "".join(filter(str.isdigit, order.get("customer_phone", "")))
            if order_phone and (clean_phone.endswith(order_phone) or order_phone.endswith(clean_phone)):
                results.append(order)
        return results

order_service = OrderService()
