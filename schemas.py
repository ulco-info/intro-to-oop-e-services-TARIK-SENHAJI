
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict


# ── DTO Interne : contrat entre Data Engineering et Data Science ────────────

class PricePoint(BaseModel):
    """
    Représente UNE annonce brute normalisée issue du scraper.

    Toute l'équipe (Jaddi, El Khelyfy, Affoudji, Tafoughalti) se base
    sur ce modèle comme source de vérité. Si le scraper change le nom
    d'une clé, Pydantic lèvera immédiatement une ValidationError.
    """
    title: str = Field(..., description="Titre de l'annonce produit")
    # FIX: le @field_validator `price_must_be_positive` ci-dessous était redondant
    # avec `gt=0` qui applique déjà la même contrainte via le système natif de Pydantic.
    # On conserve uniquement `gt=0` — plus déclaratif, plus performant, zéro duplication.
    price: float = Field(..., gt=0, description="Prix en euros, doit être > 0")
    currency: str = Field(default="EUR", description="Devise du prix")
    source: Optional[str] = Field(default=None, description="Plateforme d'origine (ex: leboncoin)")
    condition: Optional[str] = Field(default=None, description="État du produit (new, used…)")


# ── DTO Entrée : ce que le Frontend envoie ─────────────────────────────────

class ProductRequest(BaseModel):
    product_name: str = Field(..., min_length=2, description="Nom du produit à analyser")
    strategy: str = Field(
        default="balanced",
        description="Stratégie de prix : fast_sale | max_profit | balanced"
    )
    condition: Optional[str] = Field(default="new", description="État du produit recherché")

    @field_validator("strategy")
    @classmethod
    def strategy_must_be_valid(cls, v: str) -> str:
        allowed = {"fast_sale", "max_profit", "balanced"}
        if v not in allowed:
            raise ValueError(f"Stratégie invalide. Valeurs acceptées : {allowed}")
        return v


# ── DTO Sortie : ce que l'API renvoie au Frontend ──────────────────────────

class PriceResponse(BaseModel):
    product_name: str
    recommended_price: float
    currency: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    justification: str
    market_stats: Dict[str, float]


# ── DTO Santé : réponse de l'endpoint /health ──────────────────────────────

class ComponentStatus(BaseModel):
    status: str = Field(..., description="'ok' | 'degraded' | 'unreachable'")
    latency_ms: Optional[float] = Field(default=None, description="Latence du ping en ms")
    detail: Optional[str] = Field(default=None, description="Message d'erreur éventuel")


class HealthResponse(BaseModel):
    status: str = Field(..., description="'healthy' | 'degraded' | 'unhealthy'")
    components: Dict[str, ComponentStatus]
