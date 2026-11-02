import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.webhook import router as webhook_router
from app.knowledge.catalog import catalog_service
from app.knowledge.policies import policy_service
from app.knowledge.orders import order_service

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("emporio_musica_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("==================================================")
    logger.info(f"🎸 Starting Agent for {settings.COMPANY_NAME}")
    logger.info(f"📦 Loaded {len(catalog_service.get_all())} products in catalog")
    logger.info(f"📋 Loaded {len(order_service._orders)} orders in database")
    logger.info(f"ℹ️ Policies configured: {list(policy_service.get_all().keys())}")
    logger.info(f"🌐 Server running on http://{settings.HOST}:{settings.PORT}")
    logger.info("==================================================")
    yield
    logger.info("Shutting down Empório da Música Agent...")

app = FastAPI(
    title=f"{settings.COMPANY_NAME} - WhatsApp Agent API",
    description="Intelligent WhatsApp text assistant with catalog search, policy enforcement, order tracking, and guardrails.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local web testing if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(webhook_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "company": settings.COMPANY_NAME,
        "assistant_name": "Afinado",
        "endpoints": {
            "webhook_verification": "GET /webhook",
            "webhook_events": "POST /webhook",
            "health": "GET /health"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "catalog_items": len(catalog_service.get_all()),
        "active_orders": len(order_service._orders),
        "llm_model": settings.LLM_MODEL,
        "llm_base_url": settings.LLM_BASE_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
