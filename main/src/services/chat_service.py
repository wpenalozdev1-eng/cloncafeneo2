from main.src.domain.schemas import ChatRequest, ChatResponse
from main.src.infrastructure.model_factory import AIModelFactory
from main.src.infrastructure.context_loader import ContextLoader
from pathlib import Path
import re


class ChatService:
    def __init__(self, context: str):
        self._context = context
        self.menu_prices, self.combo_prices = self._load_prices_from_menu()

    def _load_prices_from_menu(self):
        menu_path = Path('main/knowledge/menu.md')
        menu_prices = {}
        combo_prices = {}

        if not menu_path.exists():
            return menu_prices, combo_prices

        with open(menu_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Extraer items con formatos '1. Nombre: $X' y combos '- Combo ...: ... $X'
        item_pattern = re.compile(r"\d+\.\s*([^:]+):\s*\$(\d+(?:\.\d+)?)", re.IGNORECASE)
        combo_pattern = re.compile(r"-\s*(Combo [^:]+):.*?\$(\d+(?:\.\d+)?)", re.IGNORECASE)

        for name, price in item_pattern.findall(text):
            menu_prices[name.strip().lower()] = float(price)

        for name, price in combo_pattern.findall(text):
            combo_prices[name.strip().lower()] = float(price)

        return menu_prices, combo_prices

    def _normalize(self, text: str) -> str:
        return (text or "").strip().lower()

    def _find_last_recommendation(self, history):
        if not history:
            return None
        for msg in reversed(history):
            if msg.role in ["assistant", "bot"] and msg.content:
                text = self._normalize(msg.content)
                for combo_name in self.combo_prices:
                    if combo_name in text:
                        return combo_name
                for item_name in self.menu_prices:
                    if item_name in text:
                        return item_name
        return None

    def _price_for(self, product: str):
        if not product:
            return None
        product = self._normalize(product)
        if product in self.combo_prices:
            return self.combo_prices[product]
        if product in self.menu_prices:
            return self.menu_prices[product]
        return None

    def respond(self, request: ChatRequest) -> ChatResponse:
        question = self._normalize(request.pregunta)
        history = request.historial or []

        if any(keyword in question for keyword in ["que vale", "precio", "cuánto cuesta", "cuanto cuesta", "cuánto es", "cual es el precio", "cual es el valor"]):
            # Intenta inferir producto del último contexto cuando el usuario pregunta precios de seguimiento
            selected = self._find_last_recommendation(history)
            if selected:
                price = self._price_for(selected)
                if price:
                    respuesta = f"El {selected} cuesta ${price:.2f}."
                    return ChatResponse(respuesta=respuesta, provider=request.provider, tokens_usados=None)
            respuesta = "¿Qué producto o combo te interesa saber el precio?"
            return ChatResponse(respuesta=respuesta, provider=request.provider, tokens_usados=None)

        # Siempre intenta mantener el contexto del menú y la coherencia
        adapter = AIModelFactory.create(request.provider)
        respuesta, tokens = adapter.complete(self._context, request.pregunta, history)

        # Asegurar que si hay una recomendación, se mencione el precio al final
        if "recomiendo" in question or "recomend" in question or "comb" in question:
            for combo_name, combo_price in self.combo_prices.items():
                if combo_name in self._normalize(respuesta):
                    if f"${combo_price:.2f}" not in respuesta:
                        respuesta = respuesta.strip().rstrip('.') + f"; por solo ${combo_price:.2f}."
                        break

        return ChatResponse(respuesta=respuesta, provider=request.provider, tokens_usados=tokens)