import asyncio
import sys

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

    print("=" * 65)
    print(f"🎵 BEM-VINDO AO SIMULADOR DE CHAT DO {settings.COMPANY_NAME.upper()} 🎵")
    print("=" * 65)
    print("Assistente: Afinado (Consultor Virtual Musical)")
    print(f"Catálogo carregado: {len(catalog_service.get_all())} produtos")
    print(f"Políticas carregadas: {list(policy_service.get_all().keys())}")
    print(f"Pedidos de teste: {len(order_service._orders)} cadastrados")
    print("\nComandos especiais:")
    print("  /catalog   -> Ver todos os produtos do estoque")
    print("  /orders    -> Ver pedidos cadastrados para teste de rastreio")
    print("  /policies  -> Ver resumo das políticas da loja")
    print("  /clear     -> Limpar o histórico da conversa atual")
    print("  sair       -> Encerrar o simulador")
    print("=" * 65)
    print("\nSugestões de perguntas para testar:")
    print('  1. "Olá! Quais violões para iniciantes vocês têm e quanto custam?"')
    print('  2. "Quais são as opções de pagamento e parcelamento?"')
    print('  3. "Onde fica a loja física e qual o horário de funcionamento?"')
    print('  4. "Vocês fazem regulagem de guitarra aí na loja?"')
    print('  5. "Qual o status do meu pedido PED-1002?"')
    print('  6. "Vocês vendem máquina de lavar roupa?" (teste de guardrail/fora do escopo)')
    print('  7. "Gostaria de falar com um atendente humano." (teste de transbordo)')
    print("-" * 65)

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
                print("\n📦 PRODUTOS EM ESTOQUE:")
                for p in catalog_service.get_all():
                    print(f"  • [{p['id']}] {p['name']} - R$ {p['price']:.2f} (Estoque: {p['stock']})")
                continue

            if user_input.lower() == "/orders":
                print("\n📋 PEDIDOS PARA TESTE:")
                for o in order_service._orders:
                    print(f"  • {o['order_id']} | {o['customer_name']} | Status: {o['status']} | Rastreio: {o.get('tracking_code')}")
                continue

            if user_input.lower() == "/policies":
                print("\n📜 RESUMO DAS POLÍTICAS:")
                print(policy_service.get_summary_text())
                continue

            print("\n[Afinado está digitando...]")
            response = await agent_brain.handle_message(session_id=session_id, user_text=user_input)

            print(f"\nAfinado (WhatsApp):\n{response}")
            print("-" * 65)

        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o simulador. Até logo! 🎶")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
