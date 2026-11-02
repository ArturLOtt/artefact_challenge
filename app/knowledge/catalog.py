import json
import logging
from typing import List, Dict, Any, Optional
from app.database.db import db_service

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self):
        self.db = db_service

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                p.product_id,
                p.name,
                p.price_brl,
                p.stock_quantity,
                p.status,
                p.description,
                p.specs,
                c.name as category_name,
                pr.discount_percent as active_discount,
                pr.description as promotion_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
            WHERE 1=1
        """
        params = []

        if in_stock_only:
            sql += " AND p.stock_quantity > 0 AND p.status = 'active'"

        if max_price is not None:
            sql += " AND CAST(p.price_brl AS REAL) <= ?"
            params.append(float(max_price))

        if category:
            sql += " AND (LOWER(c.name) LIKE ? OR LOWER(p.name) LIKE ?)"
            cat_param = f"%{category.strip().lower()}%"
            params.extend([cat_param, cat_param])

        if query:
            tokens = [t.strip().lower() for t in query.split() if t.strip()]
            for token in tokens:
                sql += """ AND (
                    LOWER(p.name) LIKE ? 
                    OR LOWER(p.description) LIKE ? 
                    OR LOWER(c.name) LIKE ?
                    OR LOWER(p.specs) LIKE ?
                )"""
                t_param = f"%{token}%"
                params.extend([t_param, t_param, t_param, t_param])

        sql += " ORDER BY p.price_brl ASC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            orig_price = float(r["price_brl"])
            active_disc = float(r["active_discount"]) if r["active_discount"] else 0.0

            if active_disc > 0:
                final_price = round(orig_price * (1.0 - active_disc / 100.0), 2)
                pix_price = final_price  # PIX doesn't cumulate with promotions
                has_promo = True
            else:
                final_price = orig_price
                pix_price = round(orig_price * 0.95, 2)  # 5% PIX discount on regular price
                has_promo = False

            try:
                specs_dict = json.loads(r["specs"]) if r["specs"] else {}
            except Exception:
                specs_dict = {}

            results.append({
                "product_id": r["product_id"],
                "name": r["name"],
                "category": r["category_name"],
                "price": orig_price,
                "final_price": final_price,
                "pix_price": pix_price,
                "has_active_promotion": has_promo,
                "promotion_discount": f"{active_disc:.0f}%" if has_promo else None,
                "promotion_name": r["promotion_name"] if has_promo else None,
                "stock": r["stock_quantity"],
                "description": r["description"],
                "specs": specs_dict
            })

        return results

    def get_product_details(self, identifier: str) -> Optional[Dict[str, Any]]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        row = None
        clean_id = "".join(filter(str.isdigit, identifier))
        if clean_id:
            cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.product_id = ?
            """, (int(clean_id),))
            row = cursor.fetchone()

        if not row:
            cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE LOWER(p.name) LIKE ?
                ORDER BY LENGTH(p.name) ASC LIMIT 1
            """, (f"%{identifier.strip().lower()}%",))
            row = cursor.fetchone()

        if not row:
            return None

        prod_id = row["product_id"]
        price = float(row["price_brl"])

        cursor.execute("""
            SELECT promotion_id, discount_percent, description, is_active
            FROM promotions
            WHERE product_id = ?
        """, (prod_id,))
        promotions = cursor.fetchall()

        active_promo = None
        expired_promos = []
        for p in promotions:
            p_data = {
                "promotion_id": p["promotion_id"],
                "discount_percent": float(p["discount_percent"]),
                "description": p["description"],
                "is_active": bool(p["is_active"])
            }
            if p["is_active"] == 1:
                active_promo = p_data
            else:
                expired_promos.append(p_data)

        if active_promo:
            final_price = round(price * (1.0 - active_promo["discount_percent"] / 100.0), 2)
            pix_price = final_price
        else:
            final_price = price
            pix_price = round(price * 0.95, 2)

        try:
            specs = json.loads(row["specs"]) if row["specs"] else {}
        except Exception:
            specs = {}

        return {
            "product_id": prod_id,
            "name": row["name"],
            "category": row["category_name"],
            "price": price,
            "final_price": final_price,
            "pix_price": pix_price,
            "stock": row["stock_quantity"],
            "status": row["status"],
            "description": row["description"],
            "specs": specs,
            "active_promotion": active_promo,
            "expired_promotions": expired_promos
        }

    def get_all(self) -> List[Dict[str, Any]]:
        """Returns all products in the catalog."""
        return self.search_products(query=None, in_stock_only=False, limit=500)

    def list_categories(self) -> List[Dict[str, Any]]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, name, description FROM categories ORDER BY category_id ASC")
        return [dict(r) for r in cursor.fetchall()]

catalog_service = CatalogService()
