
from abc import ABC, abstractmethod
from typing import List, Dict
from schemas import PricePoint


# ── Équipe Data Engineering (Jaddi, El Khelyfy, El Jmili) ──────────────────

class MarketProvider(ABC):
    @abstractmethod
    async def fetch_listings(self, product_name: str) -> List[PricePoint]:
        """
        Scrape le marché et retourne une liste d'annonces normalisées.
        Doit lever MarketUnreachableError si la source est inaccessible,
        ou InsufficientDataError si le nombre d'annonces est trop faible.
        """
        pass

    async def ping(self) -> bool:
        """
        Vérifie que la source de données est joignable (utilisé par /health).
        Retourne True si ok, False sinon. À surcharger si possible.
        """
        return True


# ── Équipe Data Science (Affoudji, Tafoughalti, Younoussa) ─────────────────

class MarketAnalyzer(ABC):
    @abstractmethod
    async def calculate_stats(self, listings: List[PricePoint]) -> Dict[str, float]:
        """
        Calcule les statistiques de marché à partir des annonces validées.
        Retourne : {mean: float, median: float, min: float, max: float, count: int}
        Doit lever StatisticsError en cas d'anomalie de calcul.
        """
    pass


# ── Équipe IA (Boukechouch, El Yousfi, Elhaddouchi) ────────────────────────

class PricingAgent(ABC):
    @abstractmethod
    async def get_price_advice(self, stats: Dict[str, float], strategy: str) -> Dict:
        """
        Consulte le LLM pour obtenir un conseil de prix.
        Retourne : {price: float, justification: str, confidence: float}
        Doit lever AIAgentError si l'API LLM est indisponible ou la réponse invalide.
        """
        pass

    async def ping(self) -> bool:
        """
        Vérifie que l'API de l'agent IA est joignable (utilisé par /health).
        Retourne True si ok, False sinon. À surcharger avec un vrai appel léger.
        """
        return True
