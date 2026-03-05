import logging
from typing import List
from pydantic import ValidationError

from interfaces import MarketProvider, MarketAnalyzer, PricingAgent
from schemas import ProductRequest, PriceResponse, PricePoint
from exceptions import (
    DataContractError,
    InsufficientDataError,
    MarketUnreachableError,
    StatisticsError,
    AIAgentError,
)

logger = logging.getLogger(__name__)

# Seuil minimum d'annonces pour que l'analyse soit jugée fiable
MIN_LISTINGS = 2


class PriceController:
    def __init__(
        self,
        scraper: MarketProvider,
        analyzer: MarketAnalyzer,
        ai_agent: PricingAgent,
    ):
        self.scraper = scraper
        self.analyzer = analyzer
        self.ai_agent = ai_agent

    async def process_request(self, request: ProductRequest) -> PriceResponse:
        # FIX: print() remplacé par logger.info() — intégration correcte avec le
        # framework de logging (niveaux, handlers, formatters, rotation de fichiers…).
        logger.info("Début du traitement pour '%s'", request.product_name)

        # ── ÉTAPE 1 : Scraping (Équipe Jaddi / El Khelyfy) ─────────────────
        # Le scraper peut lever MarketUnreachableError → propagé tel quel.
        raw_data = await self.scraper.fetch_listings(request.product_name)

        # Vérification du seuil minimum d'annonces
        if not raw_data or len(raw_data) < MIN_LISTINGS:
            raise InsufficientDataError(
                product_name=request.product_name,
                found=len(raw_data) if raw_data else 0,
                minimum=MIN_LISTINGS,
            )

        # ── Validation du contrat DTO (Contract Testing QE Salma/Chaimaa) ──
        # On accepte aussi bien des PricePoint déjà construits que des dict bruts.
        validated_listings: List[PricePoint] = []
        for idx, item in enumerate(raw_data):
            try:
                point = item if isinstance(item, PricePoint) else PricePoint(**item)
                validated_listings.append(point)
            except (ValidationError, TypeError) as exc:
                raise DataContractError(
                    f"Annonce #{idx} invalide : {exc}"
                ) from exc

        logger.info("%d annonce(s) validée(s).", len(validated_listings))

        # ── ÉTAPE 2 : Statistiques (Équipe Affoudji / Tafoughalti) ─────────
        # Le calculateur peut lever StatisticsError → propagé tel quel.
        stats = await self.analyzer.calculate_stats(validated_listings)

        # ── ÉTAPE 3 : Conseil IA (Équipe Boukechouch / El Yousfi) ──────────
        # L'agent peut lever AIAgentError → propagé tel quel.
        ai_result = await self.ai_agent.get_price_advice(stats, request.strategy)

        # ── ÉTAPE 4 : Construction de la réponse ───────────────────────────
        return PriceResponse(
            product_name=request.product_name,
            recommended_price=ai_result["price"],
            currency="EUR",
            confidence_score=ai_result["confidence"],
            justification=ai_result["justification"],
            market_stats=stats,
        )
