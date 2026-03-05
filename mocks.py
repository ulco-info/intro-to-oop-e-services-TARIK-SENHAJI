
from interfaces import MarketProvider, MarketAnalyzer, PricingAgent
from schemas import PricePoint
from typing import List, Dict
import asyncio
import statistics


class MockScraper(MarketProvider):
    async def fetch_listings(self, product_name: str) -> List[PricePoint]:
        await asyncio.sleep(0.1)  # Simulation d'un délai réseau réduit
        return [
            PricePoint(title=f"{product_name} - Annonce 1", price=100.0, source="mock"),
            PricePoint(title=f"{product_name} - Annonce 2", price=120.0, source="mock"),
            PricePoint(title=f"{product_name} - Annonce 3", price=110.0, source="mock"),
        ]

    async def ping(self) -> bool:
        # Le mock est toujours disponible
        return True


class MockAnalyzer(MarketAnalyzer):
    # FIX: méthode marquée async pour respecter l'interface MarketAnalyzer
    # et permettre l'appel `await self.analyzer.calculate_stats(...)` dans le contrôleur.
    # Sans `async`, Python levait TypeError: object dict can't be used in 'await' expression.
    async def calculate_stats(self, listings: List[PricePoint]) -> Dict[str, float]:
        prices = [p.price for p in listings]
        return {
            "mean": round(statistics.mean(prices), 2),
            "median": round(statistics.median(prices), 2),
            "min": min(prices),
            "max": max(prices),
            "count": float(len(prices)),
        }


class MockAI(PricingAgent):
    async def get_price_advice(self, stats: Dict[str, float], strategy: str) -> Dict:
        mean = stats.get("mean", 100.0)
        multipliers = {"fast_sale": 0.95, "balanced": 0.98, "max_profit": 1.05}
        factor = multipliers.get(strategy, 0.98)
        return {
            "price": round(mean * factor, 2),
            "justification": (
                f"Stratégie '{strategy}' : prix recommandé à {factor*100:.0f}% "
                f"de la moyenne de marché ({mean}€)."
            ),
            "confidence": 0.95,
        }

    async def ping(self) -> bool:
        return True
