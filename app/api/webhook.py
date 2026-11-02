import logging
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks, Response
from app.config import settings
from app.agent.brain import agent_brain
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])

@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Verification endpoint required by Meta Cloud API when configuring webhooks.
    """
    logger.info(f"Verification request: mode={hub_mode}, token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verification token matched successfully!")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning("Webhook verification failed: Invalid verify token or mode mismatch.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")

async def process_incoming_message(sender_id: str, message_id: str, message_text: str):
    """
    Background worker that runs the agent logic and sends the response back to WhatsApp.
    """
    try:
        # 1. Mark incoming message as read
        if message_id:
            await whatsapp_service.mark_message_as_read(message_id)

        # 2. Get AI Agent response with tool execution
        reply_text = await agent_brain.handle_message(session_id=sender_id, user_text=message_text)

        # 3. Deliver answer back to the customer on WhatsApp
        await whatsapp_service.send_text_message(to_phone=sender_id, text=reply_text)

    except Exception as e:
        logger.error(f"Error processing background message for {sender_id}: {e}", exc_info=True)

@router.post("")
async def handle_incoming_events(request: Request, background_tasks: BackgroundTasks):
    """
    Handles incoming events from WhatsApp (messages, statuses, delivery receipts).
    Meta requires this endpoint to return 200 OK rapidly (<3s), so processing is offloaded.
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"Invalid JSON payload: {e}")
        return {"status": "ignored"}

    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])

            for msg in messages:
                sender_id = msg.get("from")
                msg_id = msg.get("id")
                msg_type = msg.get("type")

                # Handle text messages
                if msg_type == "text":
                    body_text = msg.get("text", {}).get("body", "").strip()
                    if body_text and sender_id:
                        logger.info(f"Received text message from {sender_id}: '{body_text}'")
                        background_tasks.add_task(
                            process_incoming_message,
                            sender_id=sender_id,
                            message_id=msg_id,
                            message_text=body_text
                        )
                elif msg_type in ["audio", "image", "document", "video", "sticker"]:
                    # Polite notification for unsupported media types
                    background_tasks.add_task(
                        whatsapp_service.send_text_message,
                        to_phone=sender_id,
                        text="Olá! No momento ainda não consigo ouvir áudios ou visualizar mídias por aqui. "
                             "Poderia nos mandar sua dúvida em formato de texto? Muito obrigado! 🎶"
                    )

    # Always return 200 OK immediately to WhatsApp
    return {"status": "EVENT_RECEIVED"}
