import logging
from typing import Dict, Any, Optional, List
from app.database.db import db_service

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self.db = db_service

    def track_order(self, identifier: str) -> Optional[Dict[str, Any]]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        clean_val = identifier.strip().upper()
        numeric_id = None
        if clean_val.startswith("PED-") or clean_val.isdigit():
            digits = "".join(filter(str.isdigit, clean_val))
            if digits:
                numeric_id = int(digits)

        if numeric_id is not None:
            cursor.execute("""
                SELECT 
                    o.order_id,
                    o.order_date,
                    o.status,
                    o.total_brl,
                    o.payment_method,
                    o.tracking_code,
                    o.estimated_delivery,
                    o.notes,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.city as customer_city
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_id = ? OR UPPER(o.tracking_code) = ?
            """, (numeric_id, clean_val))
        else:
            cursor.execute("""
                SELECT 
                    o.order_id,
                    o.order_date,
                    o.status,
                    o.total_brl,
                    o.payment_method,
                    o.tracking_code,
                    o.estimated_delivery,
                    o.notes,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.city as customer_city
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE UPPER(o.tracking_code) = ?
            """, (clean_val,))

        order = cursor.fetchone()
        if not order:
            return None

        cursor.execute("""
            SELECT 
                oi.quantity,
                p.product_id,
                p.name as product_name,
                p.price_brl
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (order["order_id"],))
        items = cursor.fetchall()

        items_list = [
            {
                "product_id": it["product_id"],
                "name": it["product_name"],
                "quantity": it["quantity"],
                "unit_price": float(it["price_brl"])
            }
            for it in items
        ]

        status_pt = {
            "delivered": "Entregue ao destinatário",
            "shipped": "Em transporte / A caminho",
            "confirmed": "Pagamento confirmado (em separação no estoque)",
            "pending": "Aguardando confirmação de pagamento",
            "cancelled": "Cancelado"
        }.get(order["status"], order["status"])

        return {
            "order_id": f"PED-{order['order_id']}",
            "order_date": order["order_date"],
            "status_raw": order["status"],
            "status": status_pt,
            "total_brl": float(order["total_brl"]),
            "payment_method": order["payment_method"],
            "tracking_code": order["tracking_code"] if order["tracking_code"] else None,
            "estimated_delivery": order["estimated_delivery"] if order["estimated_delivery"] else None,
            "notes": order["notes"] if order["notes"] else None,
            "customer_name": order["customer_name"],
            "city": order["customer_city"],
            "items": items_list
        }

    def get_orders_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        clean_digits = "".join(filter(str.isdigit, phone))
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.order_id 
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE REPLACE(REPLACE(REPLACE(REPLACE(c.phone, '(', ''), ')', ''), '-', ''), ' ', '') LIKE ?
        """, (f"%{clean_digits[-8:]}%",))

        rows = cursor.fetchall()
        results = []
        for r in rows:
            details = self.track_order(str(r["order_id"]))
            if details:
                results.append(details)
        return results

    @property
    def _orders(self) -> List[Dict[str, Any]]:
        """Returns all registered orders for administration and status checks."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                o.order_id, 
                o.customer_id, 
                o.order_date, 
                o.status, 
                o.total_brl, 
                o.tracking_code, 
                c.name as customer_name 
            FROM orders o 
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_id ASC
        """)
        return [dict(r) for r in cursor.fetchall()]

    def get_all(self) -> List[Dict[str, Any]]:
        return self._orders

order_service = OrderService()
