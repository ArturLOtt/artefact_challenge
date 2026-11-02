import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_version = settings.WHATSAPP_API_VERSION
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.token = settings.WHATSAPP_TOKEN
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"

    async def send_text_message(self, to_phone: str, text: str) -> Optional[Dict[str, Any]]:
        """
        Sends a standard text message back to the customer on WhatsApp via Meta Cloud API.
        """
        if not self.token or "your_" in self.token:
            logger.warning(
                f"[SIMULATED OUTBOUND WHATSAPP] To: {to_phone} | Message: {text[:80]}..."
            )
            return {"status": "simulated", "to": to_phone}

        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    logger.info(f"Message sent successfully to {to_phone}")
                    return response.json()
                else:
                    logger.error(
                        f"Failed to send WhatsApp message. HTTP {response.status_code}: {response.text}"
                    )
                    return None
        except Exception as e:
            logger.error(f"Network error sending WhatsApp message: {e}")
            return None

    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Marks an incoming message as read (blue check marks).
        """
        if not self.token or "your_" in self.token:
            return True

        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.warning(f"Could not mark message {message_id} as read: {e}")
            return False

whatsapp_service = WhatsAppService()
