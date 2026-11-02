import asyncio
import sys

# Configure UTF-8 on Windows consoles to prevent encoding issues with emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.config import settings
from app.agent.brain import agent_brain
from app.knowledge.catalog import catalog_service
from app.knowledge.policies import policy_service
from app.knowledge.orders import order_service

async def main():
    session_id = "test_user_cli"

    all_products = catalog_service.get_all()
    all_orders = order_service.get_all()

    print("=" * 68)
    print(f"🎵 BEM-VINDO AO SIMULADOR DE CHAT DO {settings.COMPANY_NAME.upper()} 🎵")
    print("=" * 68)
    print("Assistente: Afinado (Consultor Virtual Musical)")
    print(f"Catálogo carregado: {len(all_products)} produtos cadastrados")
    print(f"Pedidos na base: {len(all_orders)} pedidos")
    print(f"Políticas carregadas: {list(policy_service.get_all().keys())}")
    print("\nComandos especiais:")
    print("  /catalog   -> Ver produtos do estoque")
    print("  /orders    -> Ver pedidos cadastrados para teste de rastreio")
    print("  /policies  -> Ver resumo das políticas da loja")
    print("  /clear     -> Limpar o histórico da conversa atual")
    print("  sair       -> Encerrar o simulador")
    print("=" * 68)
    print("\nSugestões para testar o fluxo de navegação e atendimento:")
    print('  1. "Olá!" -> Menu inicial com os 4 Grandes Tópicos')
    print('  2. "Quais opções de violões disponíveis custando até R$1000?" -> Catálogo + follow-up')
    print('  3. "Onde fica a loja e qual o horário de funcionamento?" -> Localização + SLA')
    print('  4. "Quanto custa o Takamine GD20?" -> Preço + alerta de promoção vencida')
    print('  5. "Me arrependi da minha compra, posso devolver meu pedido?" -> Política de troca')
    print('  6. "Qual o status do meu pedido PED-1?" (ou rastreio "BRCX9876543BR")')
    print('  7. "Vocês vendem encordoamento ou palhetas?" -> Restrição de acessórios')
    print('  8. (A partir da 4ª pergunta): Teste de transbordo proativo para atendente humano!')
    print("-" * 68)

    while True:
        try:
            user_input = input("\nVocê (Cliente): ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\nEncerrando o simulador. Até logo! 🎶")
                break

            if user_input.lower() == "/clear":
                agent_brain.clear_history(session_id)
                print("🧹 Histórico da conversa foi reiniciado com sucesso!")
                continue

            if user_input.lower() == "/catalog":
                print("\n📦 PRODUTOS EM ESTOQUE (Amostra):")
                for p in catalog_service.get_all()[:10]:
                    pid = p.get("product_id") or p.get("id")
                    print(f"  • [{pid}] {p['name']} - R$ {p['price']:.2f} (Estoque: {p['stock']})")
                print("  ... e mais modelos no catálogo.")
                continue

            if user_input.lower() == "/orders":
                print("\n📋 PEDIDOS PARA TESTE:")
                for o in order_service.get_all()[:6]:
                    trk = o.get('tracking_code') or 'Em processamento'
                    print(f"  • Pedido PED-{o['order_id']} | {o.get('customer_name', 'Cliente')} | Status: {o['status']} | Rastreio: {trk}")
                continue

            if user_input.lower() == "/policies":
                print("\n📜 RESUMO DAS POLÍTICAS:")
                print(policy_service.get_summary_text())
                continue

            print("\n[Afinado está digitando...]")
            response = await agent_brain.handle_message(session_id=session_id, user_text=user_input)

            print(f"\nAfinado (WhatsApp):\n{response}")
            print("-" * 68)

        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o simulador. Até logo! 🎶")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
