import json
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self, file_path=None):
        self.file_path = file_path or settings.PRODUCTS_FILE
        self._products: List[Dict[str, Any]] = []
        self.reload()

    def reload(self) -> None:
        """Reload products data from JSON file."""
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._products = json.load(f)
                logger.info(f"Loaded {len(self._products)} products from {self.file_path}")
            else:
                logger.warning(f"Products file not found at: {self.file_path}")
                self._products = []
        except Exception as e:
            logger.error(f"Error loading products file: {e}")
            self._products = []

    def get_all(self) -> List[Dict[str, Any]]:
        return self._products

    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Find product by unique ID (e.g. PROD-001)."""
        pid = product_id.strip().upper()
        for p in self._products:
            if p.get("id", "").upper() == pid:
                return p
        return None

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search products by keyword match across name, subtype, brand, category, and specs.
        Allows filtering by category and maximum price.
        """
        results = []
        q_tokens = [t.lower() for t in query.split()] if query else []

        for p in self._products:
            # Stock filter
            if in_stock_only and p.get("stock", 0) <= 0:
                continue

            # Price filter
            price = p.get("price", 0.0)
            if max_price is not None and price > max_price:
                continue

            # Category filter
            if category:
                cat_target = category.strip().lower()
                p_cat = p.get("category", "").lower()
                p_sub = p.get("subtype", "").lower()
                if cat_target not in p_cat and cat_target not in p_sub:
                    continue

            # Text query matching
            if q_tokens:
                searchable_text = f"{p.get('name', '')} {p.get('brand', '')} {p.get('category', '')} {p.get('subtype', '')} {p.get('specs', '')} {p.get('suitable_for', '')}".lower()
                match = any(token in searchable_text for token in q_tokens)
                if not match:
                    continue

            results.append(p)

        return results

    def list_categories(self) -> List[str]:
        categories = {p.get("category") for p in self._products if p.get("category")}
        return sorted(list(categories))

catalog_service = CatalogService()
